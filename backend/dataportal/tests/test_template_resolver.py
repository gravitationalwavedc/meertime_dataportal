"""
Test GraphQL template resolver - following the same pattern as ephemeris resolver.
Tests the _get_accessible_template method and related resolvers in queries.py.
"""

import json
import tempfile
from datetime import datetime, timedelta

import pytz
from django.contrib.auth import get_user_model
from django.test import override_settings
from graphene_django.utils.testing import GraphQLTestCase

from dataportal.models import (
    Calibration,
    Observation,
    PipelineRun,
    Project,
    ProjectMembership,
    Pulsar,
    PulsarFoldResult,
    Template,
    Toa,
)
from dataportal.tests.testing_utils import create_basic_data

User = get_user_model()


class TemplateResolverTestCase(GraphQLTestCase):
    """Test cases for template resolver logic - mirrors ephemeris resolver tests"""

    # GraphQL query to get folding template info
    FOLDING_TEMPLATE_QUERY = """
        query {{
            pulsarFoldResult(
                pulsar: "{pulsar}",
                mainProject: "MeerTIME"
                first: 10
            ) {{
                foldingTemplate {{
                    id
                    band
                    templateFile
                    createdAt
                    project {{
                        code
                    }}
                }}
                foldingTemplateIsEmbargoed
                foldingTemplateExistsButInaccessible
            }}
        }}
    """

    def setUp(self):
        """Set up test data"""
        # Create basic test data
        self.telescope, _, self.ephemeris, self.template = create_basic_data()
        self.pulsar = Pulsar.objects.get(name="J0125-2327")

        # Get the MeerTIME PTA project (code is SCI-20180516-MB-05, short is PTA)
        self.project = Project.objects.get(code="SCI-20180516-MB-05")

        # Create test users
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123", role="ADMIN"
        )
        self.project_member = User.objects.create_user(
            username="member", email="member@test.com", password="member123", role="UNRESTRICTED"
        )
        self.non_member = User.objects.create_user(
            username="nonmember", email="nonmember@test.com", password="nonmember123", role="UNRESTRICTED"
        )

        # Create project membership
        ProjectMembership.objects.create(
            user=self.project_member, project=self.project, role=ProjectMembership.RoleChoices.MEMBER
        )

        # Create a calibration object
        self.calibration = Calibration.objects.create(
            schedule_block_id="test_sb_001",
            calibration_type="flux",
            location="/test/cal/location",
        )

    def _create_observation_with_template(
        self, pulsar, project, template, utc_start, template_created_at=None, band="LBAND", create_toa=True
    ):
        """Helper to create observation with pipeline run, template, and PulsarFoldResult"""
        observation = Observation.objects.create(
            pulsar=pulsar,
            telescope=self.telescope,
            project=project,
            calibration=self.calibration,
            ephemeris=self.ephemeris,
            utc_start=utc_start,
            frequency=1284.0,
            bandwidth=856.0,
            nchan=928,
            beam=1,
            nant=64,
            nant_eff=60,
            npol=4,
            obs_type="fold",
            raj="01:25:00",
            decj="-23:27:00",
            duration=600,
            nbit=8,
            tsamp=8.0,
            fold_nbin=1024,
            fold_nchan=1024,
            fold_tsubint=10.0,
            filterbank_nbit=8,
            filterbank_npol=4,
            filterbank_nchan=928,
            filterbank_tsamp=8.0,
            filterbank_dm=9.597,
        )
        # Override band after creation using update() to bypass save() method
        # (Observation.save() recalculates band from frequency/bandwidth)
        Observation.objects.filter(id=observation.id).update(band=band)
        observation.refresh_from_db()

        pipeline_run = PipelineRun.objects.create(
            observation=observation,
            ephemeris=self.ephemeris,
            template=template,
            pipeline_name="meerpipe",
            pipeline_description="MeerTime pipeline",
            pipeline_version="3.0.0",
            created_by="test",
            job_state="Completed",
            location="/test/location",
            dm=9.597,
            dm_err=0.001,
            dm_epoch=59000.0,
            dm_chi2r=1.2,
            dm_tres=0.5,
            sn=100.0,
            flux=25.0,
            rm=10.0,
            rm_err=1.0,
            percent_rfi_zapped=0.1,
        )

        # Set template created_at if provided
        if template_created_at:
            Template.objects.filter(id=template.id).update(created_at=template_created_at)
            template.refresh_from_db()

        # Create PulsarFoldResult (required for GraphQL query to find the data)
        PulsarFoldResult.objects.create(
            observation=observation,
            pipeline_run=pipeline_run,
            pulsar=pulsar,
        )

        if create_toa:
            Toa.objects.create(
                pipeline_run=pipeline_run,
                observation=observation,
                project=project,
                ephemeris=self.ephemeris,
                template=template,
                archive="test.ar",
                freq_MHz=1284.0,
                mjd=59000.0,
                mjd_err=0.001,
                telescope="meerkat",
                dm_corrected=False,
                nsub_type="1",
                obs_nchan=1,
            )

        return observation, pipeline_run, template

    # ===== Template Authentication Tests =====

    def test_anonymous_user_cannot_access_template(self):
        """Anonymous users cannot access any templates (requires authentication)"""
        now = datetime.now(tz=pytz.UTC)

        # Create template for this specific pulsar/project/band combination
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test_anon.std",
        )

        # Create public (non-embargoed) template - 600 days old
        template_created_at = now - timedelta(days=600)
        utc_start = now - timedelta(days=600)

        self._create_observation_with_template(
            self.pulsar, self.project, template, utc_start, template_created_at=template_created_at
        )

        # Query as anonymous user (not logged in)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Anonymous users cannot access templates, so foldingTemplate should be None
        # but foldingTemplateExistsButInaccessible should be True
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["pulsarFoldResult"]["foldingTemplate"])
        self.assertTrue(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])

    def test_authenticated_user_can_access_public_template(self):
        """Authenticated users can access non-embargoed templates"""
        now = datetime.now(tz=pytz.UTC)

        # Create template for this specific pulsar/project/band combination
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test_auth.std",
        )

        # Create public (non-embargoed) template - 600 days old
        template_created_at = now - timedelta(days=600)
        utc_start = now - timedelta(days=600)

        observation, pipeline_run, template = self._create_observation_with_template(
            self.pulsar, self.project, template, utc_start, template_created_at=template_created_at, band="LBAND"
        )

        # Query as authenticated non-member
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should see the template
        self.assertNotIn("errors", content)
        folding_template = content["data"]["pulsarFoldResult"]["foldingTemplate"]
        self.assertIsNotNone(folding_template)
        self.assertEqual(folding_template["band"], "LBAND")
        self.assertFalse(content["data"]["pulsarFoldResult"]["foldingTemplateIsEmbargoed"])

    # ===== Embargo Tests =====

    def test_embargoed_template_blocked_for_non_member(self):
        """Non-members cannot access embargoed templates"""
        now = datetime.now(tz=pytz.UTC)

        # Create template for this specific pulsar/project/band combination
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test_embargo_non.std",
        )

        # Create embargoed template - 30 days old
        template_created_at = now - timedelta(days=30)
        utc_start = now - timedelta(days=30)

        self._create_observation_with_template(
            self.pulsar, self.project, template, utc_start, template_created_at=template_created_at
        )

        # Query as authenticated non-member
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should NOT see the template
        self.assertNotIn("errors", content)
        folding_template = content["data"]["pulsarFoldResult"]["foldingTemplate"]
        self.assertIsNone(folding_template)

        # But should indicate templates exist but are inaccessible
        self.assertTrue(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])

    def test_embargoed_template_accessible_for_member(self):
        """Project members can access embargoed templates from their project"""
        now = datetime.now(tz=pytz.UTC)

        # Create template for this specific pulsar/project/band combination
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test_embargo_mem.std",
        )

        # Create embargoed template - 30 days old
        template_created_at = now - timedelta(days=30)
        utc_start = now - timedelta(days=30)

        self._create_observation_with_template(
            self.pulsar, self.project, template, utc_start, template_created_at=template_created_at
        )

        # Query as project member
        self.client.force_login(self.project_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should see the embargoed template
        self.assertNotIn("errors", content)
        folding_template = content["data"]["pulsarFoldResult"]["foldingTemplate"]
        self.assertIsNotNone(folding_template)
        self.assertEqual(folding_template["band"], "LBAND")
        self.assertTrue(content["data"]["pulsarFoldResult"]["foldingTemplateIsEmbargoed"])
        self.assertFalse(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])

    def test_superuser_can_access_embargoed_template(self):
        """Superusers can access all embargoed templates"""
        now = datetime.now(tz=pytz.UTC)

        # Create template for this specific pulsar/project/band combination
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test_super.std",
        )

        # Create embargoed template - 30 days old
        template_created_at = now - timedelta(days=30)
        utc_start = now - timedelta(days=30)

        self._create_observation_with_template(
            self.pulsar, self.project, template, utc_start, template_created_at=template_created_at
        )

        # Query as superuser
        self.client.force_login(self.superuser)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should see the embargoed template
        self.assertNotIn("errors", content)
        folding_template = content["data"]["pulsarFoldResult"]["foldingTemplate"]
        self.assertIsNotNone(folding_template)
        self.assertTrue(content["data"]["pulsarFoldResult"]["foldingTemplateIsEmbargoed"])

    # ===== Template Selection Tests (Most Recent) =====

    def test_returns_most_recent_accessible_template(self):
        """Returns the most recent template the user can access"""
        now = datetime.now(tz=pytz.UTC)

        # Create old public template (beyond embargo)
        template1 = Template.objects.create(
            pulsar=self.pulsar, project=self.project, band="LBAND", template_file="old.std"
        )
        template1_created_at = now - timedelta(days=600)  # 600 days > 548 day embargo
        Template.objects.filter(id=template1.id).update(created_at=template1_created_at)
        template1.refresh_from_db()

        utc_start1 = now - timedelta(days=600)
        self._create_observation_with_template(
            self.pulsar, self.project, template1, utc_start1, template_created_at=None
        )

        # Create newer public template (also beyond embargo)
        template2 = Template.objects.create(
            pulsar=self.pulsar, project=self.project, band="LBAND", template_file="new.std"
        )
        template2_created_at = now - timedelta(days=550)  # 550 days > 548 day embargo (just barely)
        Template.objects.filter(id=template2.id).update(created_at=template2_created_at)
        template2.refresh_from_db()

        utc_start2 = now - timedelta(days=550)
        self._create_observation_with_template(
            self.pulsar, self.project, template2, utc_start2, template_created_at=None
        )

        # Query as authenticated user
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should return the newer template
        self.assertNotIn("errors", content)
        folding_template = content["data"]["pulsarFoldResult"]["foldingTemplate"]
        self.assertIsNotNone(folding_template)
        # Check it's template2 by file name
        self.assertIn("new.std", folding_template["templateFile"])

    def test_skips_embargoed_returns_older_public_template(self):
        """If newest template is embargoed and inaccessible, returns older public template"""
        now = datetime.now(tz=pytz.UTC)

        # Create old public template
        template1 = Template.objects.create(
            pulsar=self.pulsar, project=self.project, band="LBAND", template_file="old_public.std"
        )
        template1_created_at = now - timedelta(days=600)
        Template.objects.filter(id=template1.id).update(created_at=template1_created_at)
        template1.refresh_from_db()

        utc_start1 = now - timedelta(days=600)
        self._create_observation_with_template(
            self.pulsar, self.project, template1, utc_start1, template_created_at=None
        )

        # Create newer embargoed template
        template2 = Template.objects.create(
            pulsar=self.pulsar, project=self.project, band="LBAND", template_file="new_embargoed.std"
        )
        template2_created_at = now - timedelta(days=30)
        Template.objects.filter(id=template2.id).update(created_at=template2_created_at)
        template2.refresh_from_db()

        utc_start2 = now - timedelta(days=30)
        self._create_observation_with_template(
            self.pulsar, self.project, template2, utc_start2, template_created_at=None
        )

        # Query as non-member (cannot access embargoed)
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should return the older public template, not the newer embargoed one
        self.assertNotIn("errors", content)
        folding_template = content["data"]["pulsarFoldResult"]["foldingTemplate"]
        self.assertIsNotNone(folding_template)
        self.assertFalse(content["data"]["pulsarFoldResult"]["foldingTemplateIsEmbargoed"])
        self.assertIn("old_public.std", folding_template["templateFile"])

    # ===== Edge Cases =====

    def test_no_templates_returns_none(self):
        """When no templates exist, returns None"""
        # Don't create any templates/observations

        # Query as authenticated user
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))

        content = json.loads(response.content)

        # Should return None for template
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["pulsarFoldResult"]["foldingTemplate"])
        self.assertIsNone(content["data"]["pulsarFoldResult"]["foldingTemplateIsEmbargoed"])
        self.assertFalse(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])

    def test_inactive_membership_denies_access(self):
        """Users with inactive memberships cannot access embargoed templates"""
        now = datetime.now(tz=pytz.UTC)

        # Create template for this specific pulsar/project/band combination
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test_inactive.std",
        )

        # Create embargoed template
        template_created_at = now - timedelta(days=30)
        utc_start = now - timedelta(days=30)

        self._create_observation_with_template(
            self.pulsar, self.project, template, utc_start, template_created_at=template_created_at
        )

        # Deactivate membership
        membership = ProjectMembership.objects.get(user=self.project_member, project=self.project)
        membership.is_active = False
        membership.save()

        # Query as deactivated member
        self.client.force_login(self.project_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should NOT see the embargoed template
        self.assertNotIn("errors", content)
        folding_template = content["data"]["pulsarFoldResult"]["foldingTemplate"]
        self.assertIsNone(folding_template)
        self.assertTrue(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])

    # ===== Filtering Tests (Checks that exclude invalid data) =====

    def test_ptuse_template_is_skipped(self):
        """Templates from PTUSE project should be skipped"""
        now = datetime.now(tz=pytz.UTC)

        # Create PTUSE project
        ptuse_project = Project.objects.create(
            main_project=self.project.main_project,
            code="PTUSE",
            short="PTUSE",
            embargo_period=timedelta(days=548),
        )

        # Create template for PTUSE project
        ptuse_template = Template.objects.create(
            pulsar=self.pulsar,
            project=ptuse_project,
            band="LBAND",
            template_file="ptuse_template.std",
        )

        # Create observation with PTUSE template (public, not embargoed)
        template_created_at = now - timedelta(days=600)
        utc_start = now - timedelta(days=600)
        self._create_observation_with_template(
            self.pulsar, ptuse_project, ptuse_template, utc_start, template_created_at=template_created_at
        )

        # Query as authenticated user
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # PTUSE template should be skipped, so no template returned
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["pulsarFoldResult"]["foldingTemplate"])
        self.assertFalse(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])

    def test_template_without_toas_is_skipped(self):
        """Templates from pipeline runs without TOAs should be skipped"""
        now = datetime.now(tz=pytz.UTC)

        # Create template
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="no_toas.std",
        )

        # Create observation WITHOUT TOAs (create_toa=False)
        template_created_at = now - timedelta(days=600)
        utc_start = now - timedelta(days=600)
        self._create_observation_with_template(
            self.pulsar,
            self.project,
            template,
            utc_start,
            template_created_at=template_created_at,
            create_toa=False,  # No TOAs
        )

        # Query as authenticated user
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Pipeline run without TOAs should be skipped
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["pulsarFoldResult"]["foldingTemplate"])
        self.assertFalse(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])

    def test_pipeline_run_without_template_is_skipped(self):
        """Pipeline runs without templates should be skipped"""
        now = datetime.now(tz=pytz.UTC)
        utc_start = now - timedelta(days=600)

        # Create observation with pipeline run but NO template
        observation = Observation.objects.create(
            pulsar=self.pulsar,
            telescope=self.telescope,
            project=self.project,
            calibration=self.calibration,
            ephemeris=self.ephemeris,
            utc_start=utc_start,
            frequency=1284.0,
            bandwidth=856.0,
            nchan=928,
            beam=1,
            nant=64,
            npol=4,
            obs_type="fold",
            raj="01:25:00",
            decj="-23:27:00",
            duration=600,
            nbit=8,
            tsamp=8.0,
            fold_nbin=1024,
            fold_nchan=1024,
            fold_tsubint=10.0,
        )

        pipeline_run = PipelineRun.objects.create(
            observation=observation,
            ephemeris=self.ephemeris,
            template=None,  # No template
            pipeline_name="meerpipe",
            pipeline_version="3.0.0",
            created_by="test",
            job_state="Completed",
            location="/test/location",
            dm=9.597,
            dm_err=0.001,
            sn=100.0,
            percent_rfi_zapped=0.1,
        )

        PulsarFoldResult.objects.create(
            observation=observation,
            pipeline_run=pipeline_run,
            pulsar=self.pulsar,
        )

        # Create TOA (with a valid template for the TOA foreign key)
        valid_template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="toa_template.std",
        )
        Toa.objects.create(
            pipeline_run=pipeline_run,
            observation=observation,
            project=self.project,
            ephemeris=self.ephemeris,
            template=valid_template,
            archive="test.ar",
            freq_MHz=1284.0,
            mjd=59000.0,
            mjd_err=0.001,
            telescope="meerkat",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=1,
        )

        # Query as authenticated user
        self.client.force_login(self.non_member)
        response = self.query(self.FOLDING_TEMPLATE_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Pipeline run without template should be skipped
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["pulsarFoldResult"]["foldingTemplate"])
        self.assertFalse(content["data"]["pulsarFoldResult"]["foldingTemplateExistsButInaccessible"])
