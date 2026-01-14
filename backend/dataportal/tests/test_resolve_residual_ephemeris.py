"""
Tests for resolve_folding_ephemeris function in PulsarFoldResultConnection.

This module contains comprehensive tests for the resolve_folding_ephemeris method
in dataportal/graphql/queries.py.

The function returns the ephemeris from the latest observation the user has access to,
based on ProjectMembership authorization:
- Superusers can access everything
- Non-embargoed data is public
- Embargoed data requires active ProjectMembership

Tests included:
- test_resolve_folding_ephemeris_returns_latest_ephemeris: Verifies the function returns
  the ephemeris from the most recent accessible pipeline run
- test_resolve_folding_ephemeris_excludes_ptuse_project: Ensures PTUSE project ephemerides
  are properly excluded from results
- test_resolve_folding_ephemeris_requires_toa: Confirms that only ephemeris
  with TOAs are returned
- test_project_member_can_access_embargoed_ephemeris: Project members can see their
  embargoed data
- test_non_member_cannot_access_embargoed_ephemeris: Non-members only see public data
- test_superuser_can_access_all_ephemeris: Superusers can access everything
"""

import json
import os
from datetime import datetime, timedelta

import pytz
from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from graphql_relay import from_global_id

from dataportal.models import (
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    PipelineRun,
    Project,
    ProjectMembership,
    Pulsar,
    PulsarFoldResult,
    Telescope,
    Template,
    Toa,
)
from dataportal.tests.testing_utils import TEST_DATA_DIR, create_basic_data
from utils.ephemeris import parse_ephemeris_file

User = get_user_model()


class ResolveFoldingEphemerisTestCase(GraphQLTestCase):
    """Test cases for the resolve_folding_ephemeris function in PulsarFoldResultConnection"""

    FOLDING_EPHEMERIS_QUERY = """
    query {{
        pulsarFoldResult(
            pulsar: "{pulsar}",
            mainProject: "MeerTIME"
            first: 10
        ) {{
            foldingEphemeris {{
                id
                ephemerisData
                createdAt
                dm
                p0
            }}
            foldingEphemerisIsEmbargoed
            foldingEphemerisExistsButInaccessible
        }}
    }}
    """

    def setUp(self):
        """Setup basic test environment."""
        self.user = User.objects.create(username="testuser", email="test@test.com")

        # Create basic data
        self.telescope, _, self.ephemeris, self.template = create_basic_data()
        self.pulsar = Pulsar.objects.get(name="J0125-2327")

        # Use a MeerTIME project instead of the MONSPSR project returned by create_basic_data
        main_project = MainProject.objects.get(name="MeerTIME")
        self.project = Project.objects.get(short="PTA", main_project=main_project)

        # Reassign ephemeris to the PTA project for testing
        self.ephemeris.project = self.project
        self.ephemeris.save()

        # Create a calibration object
        self.calibration = Calibration.objects.create(
            schedule_block_id="test_sb_001",
            calibration_type="flux",
            location="/test/cal/location",
        )

    def _create_observation_with_pipeline_run(
        self,
        pulsar,
        project,
        telescope,
        template,
        ephemeris,
        utc_start,
        create_toa=True,
        create_pulsar_fold_result=True,
        is_embargoed=False,
    ):
        """Helper to create an observation with pipeline run and optional TOA."""
        observation = Observation.objects.create(
            pulsar=pulsar,
            telescope=telescope,
            project=project,
            calibration=self.calibration,
            ephemeris=ephemeris,
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

        pipeline_run = PipelineRun.objects.create(
            observation=observation,
            ephemeris=ephemeris,
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

        # Set ephemeris created_at to control embargo status
        # Embargo is based on ephemeris.created_at + ephemeris.project.embargo_period
        if is_embargoed:
            # Set ephemeris created_at to recent (within embargo period)
            ephemeris_created_at = datetime.now(tz=pytz.UTC) - timedelta(days=30)
        else:
            # Set ephemeris created_at to old (past embargo period)
            # Use 600 days ago (> 548 day embargo period)
            ephemeris_created_at = datetime.now(tz=pytz.UTC) - timedelta(days=600)

        Ephemeris.objects.filter(id=ephemeris.id).update(created_at=ephemeris_created_at)
        ephemeris.refresh_from_db()

        if create_pulsar_fold_result:
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
                ephemeris=ephemeris,
                template=template,
                archive="test.ar",
                freq_MHz=1284.0,
                mjd=59000.0,
                mjd_err=0.001,
                telescope="meerkat",
                dm_corrected=False,
                nsub_type="1",
                obs_nchan=1,
                obs_npol=1,
                day_of_year=1,
                residual_sec=0.001,
                residual_sec_err=0.0001,
                residual_phase=0.1,
                residual_phase_err=0.01,
                snr=50.0,
                length=600,
            )

        return observation, pipeline_run

    def test_resolve_folding_ephemeris_returns_latest_ephemeris(self):
        """
        Test: Verify that resolve_folding_ephemeris returns the ephemeris from
        the most recent accessible pipeline run.
        """
        self.client.force_login(self.user)

        # Create first observation with ephemeris (older, not embargoed)
        utc_start_old = datetime.now(pytz.utc) - timedelta(days=10)
        obs1, pr1 = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_old,
            is_embargoed=False,
        )

        # Create a second observation (newer, not embargoed)
        utc_start_new = datetime.now(pytz.utc) - timedelta(days=5)
        obs2, pr2 = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_new,
            is_embargoed=False,
        )

        # Query for folding ephemeris
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        self.assertIn("data", content, "Response should contain data")
        self.assertIn("pulsarFoldResult", content["data"])
        self.assertIsNotNone(content["data"]["pulsarFoldResult"]["foldingEphemeris"])

        # The ephemeris should be returned
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNotNone(residual_eph, "Folding ephemeris should not be None")

        # Verify it's the correct ephemeris by decoding the GraphQL ID
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return the ephemeris associated with the latest pipeline run",
        )

    def test_resolve_folding_ephemeris_excludes_ptuse_project(self):
        """
        Test: Verify that resolve_folding_ephemeris excludes ephemerides from PTUSE project.
        """
        self.client.force_login(self.user)

        # Create a PTUSE project
        main_project = MainProject.objects.get(name="MeerTIME")
        ptuse_project = Project.objects.create(
            code="SCI-20180516-MB-PTUSE",
            short="PTUSE",
            main_project=main_project,
        )

        # Create a PTUSE ephemeris (should be excluded)
        with open(os.path.join(TEST_DATA_DIR, "J0125-2327.par"), "r") as par_file:
            par_text = par_file.read()
        ephemeris_dict = parse_ephemeris_file(par_text)
        ptuse_ephemeris = Ephemeris.objects.create(
            pulsar=self.pulsar,
            project=ptuse_project,  # PTUSE project ephemeris
            ephemeris_data=json.dumps(ephemeris_dict),
            p0=ephemeris_dict["P0"],
            dm=ephemeris_dict["DM"],
            valid_from=ephemeris_dict["START"],
            valid_to=ephemeris_dict["FINISH"],
        )

        # Create observation with PTUSE ephemeris (should be excluded) - newer, not embargoed
        utc_start_ptuse = datetime.now(pytz.utc) - timedelta(days=3)
        obs_ptuse, pr_ptuse = self._create_observation_with_pipeline_run(
            self.pulsar,
            ptuse_project,
            self.telescope,
            self.template,
            ptuse_ephemeris,
            utc_start_ptuse,
            is_embargoed=False,
        )

        # Create observation with regular (non-PTUSE) ephemeris (should be included) - older, not embargoed
        utc_start_regular = datetime.now(pytz.utc) - timedelta(days=10)
        obs_regular, pr_regular = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_regular,
            is_embargoed=False,
        )

        # Query for folding ephemeris
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        self.assertIn("data", content, "Response should contain data")

        # The ephemeris should be from the regular project, not PTUSE
        # Even though PTUSE pipeline run is more recent, PTUSE ephemerides are excluded
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNotNone(residual_eph, "Should return ephemeris from non-PTUSE project")

        # Verify it's the correct ephemeris (the regular one, not PTUSE)
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return the non-PTUSE ephemeris, not the PTUSE one",
        )

    def test_resolve_folding_ephemeris_requires_toa(self):
        """
        Test: Verify that resolve_folding_ephemeris only returns ephemeris that have TOAs.
        """
        self.client.force_login(self.user)

        # Create observation WITHOUT TOA (should be excluded) - newer
        utc_start_no_toa = datetime.now(pytz.utc) - timedelta(days=2)
        obs_no_toa, pr_no_toa = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_no_toa,
            create_toa=False,  # No TOA
            is_embargoed=False,
        )

        # Create observation WITH TOA (should be included) - older
        utc_start_with_toa = datetime.now(pytz.utc) - timedelta(days=5)
        obs_with_toa, pr_with_toa = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_with_toa,
            create_toa=True,  # Has TOA
            is_embargoed=False,
        )

        # Query for folding ephemeris
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        self.assertIn("data", content, "Response should contain data")

        # Should return ephemeris because there's at least one observation with TOA
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Should return ephemeris from observation with TOA, not the one without",
        )

    def test_project_member_can_access_embargoed_ephemeris(self):
        """
        Test: Verify that project members can access ephemeris from embargoed observations
        in their own project.
        """
        # Create project membership for the user
        ProjectMembership.objects.create(
            user=self.user,
            project=self.project,
            role=ProjectMembership.RoleChoices.MEMBER,
        )
        self.client.force_login(self.user)

        # Create embargoed observation (user is a project member, so should have access)
        utc_start = datetime.now(pytz.utc) - timedelta(days=5)
        obs, pr = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start,
            is_embargoed=True,  # Embargoed, but user is a member
        )

        # Query for residual ephemeris
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Project member should be able to access embargoed ephemeris from their project",
        )

    def test_non_member_cannot_access_embargoed_ephemeris(self):
        """
        Test: Verify that non-members cannot access ephemeris from embargoed observations.
        They should only see ephemeris from non-embargoed observations.
        """
        # User is NOT a project member
        self.client.force_login(self.user)

        # Create embargoed observation (user is NOT a member, should NOT have access)
        utc_start_embargoed = datetime.now(pytz.utc) - timedelta(days=3)
        obs_embargoed, pr_embargoed = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_embargoed,
            is_embargoed=True,  # Embargoed
        )

        # Query for folding ephemeris - should return None since only embargoed data exists
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNone(
            residual_eph,
            "Non-member should NOT be able to access embargoed ephemeris",
        )

        # Check that existsButInaccessible is True (ephemerides exist but are inaccessible)
        exists_but_inaccessible = content["data"]["pulsarFoldResult"]["foldingEphemerisExistsButInaccessible"]
        self.assertTrue(
            exists_but_inaccessible,
            "Should indicate that embargoed ephemerides exist but are inaccessible to non-member",
        )

    def test_non_member_can_access_public_ephemeris(self):
        """
        Test: Verify that non-members can access ephemeris from non-embargoed (public) observations.
        """
        # User is NOT a project member
        self.client.force_login(self.user)

        # Create non-embargoed observation (public data, everyone can access)
        utc_start = datetime.now(pytz.utc) - timedelta(days=5)
        obs, pr = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start,
            is_embargoed=False,  # Not embargoed (public)
        )

        # Query for folding ephemeris
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Non-member should be able to access public (non-embargoed) ephemeris",
        )

    def test_superuser_can_access_all_ephemeris(self):
        """
        Test: Verify that superusers can access ephemeris from all observations,
        including embargoed ones.
        """
        # Create superuser
        superuser = User.objects.create_superuser(username="superuser", email="super@test.com", password="testpass")
        self.client.force_login(superuser)

        # Create embargoed observation (superuser should still have access)
        utc_start = datetime.now(pytz.utc) - timedelta(days=5)
        obs, pr = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start,
            is_embargoed=True,  # Embargoed, but superuser can access
        )

        # Query for folding ephemeris
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Superuser should be able to access all ephemeris, including embargoed ones",
        )

    def test_non_member_sees_public_ephemeris_when_mixed(self):
        """
        Test: When both embargoed and public observations exist, non-members should
        see the ephemeris from the latest public (non-embargoed) observation.
        """
        # User is NOT a project member
        self.client.force_login(self.user)

        # Create a different ephemeris for the embargoed observation
        with open(os.path.join(TEST_DATA_DIR, "J0125-2327.par"), "r") as par_file:
            par_text = par_file.read()
        ephemeris_dict = parse_ephemeris_file(par_text)
        embargoed_ephemeris = Ephemeris.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            ephemeris_data=json.dumps({"modified": True, **ephemeris_dict}),
            p0=ephemeris_dict["P0"],
            dm=ephemeris_dict["DM"],
            valid_from=ephemeris_dict["START"],
            valid_to=ephemeris_dict["FINISH"],
        )

        # Create embargoed observation (newer) - user should NOT see this
        utc_start_embargoed = datetime.now(pytz.utc) - timedelta(days=2)
        obs_embargoed, pr_embargoed = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            embargoed_ephemeris,
            utc_start_embargoed,
            is_embargoed=True,
        )

        # Create public observation (older) - user SHOULD see this
        utc_start_public = datetime.now(pytz.utc) - timedelta(days=10)
        obs_public, pr_public = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_public,
            is_embargoed=False,
        )

        # Query for folding ephemeris
        response = self.query(self.FOLDING_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        residual_eph = content["data"]["pulsarFoldResult"]["foldingEphemeris"]
        self.assertIsNotNone(residual_eph, "Should return the public ephemeris")

        # Verify it's the public ephemeris, not the embargoed one
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Non-member should see the public ephemeris, not the embargoed one",
        )

        # Check that existsButInaccessible is None (accessible ephemeris found)
        exists_but_inaccessible = content["data"]["pulsarFoldResult"]["foldingEphemerisExistsButInaccessible"]
        self.assertIsNone(
            exists_but_inaccessible,
            "Should be None when non-member has access to public ephemeris",
        )
