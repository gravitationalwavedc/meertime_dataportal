"""
Tests for ephemeris embargo logic based on ephemeris creation date.

This module contains comprehensive tests for the corrected resolve_residual_ephemeris
embargo logic that checks ephemeris.created_at date (NOT pipeline run or observation dates).

The ephemeris represents the scientific model/knowledge of the pulsar that the project
developed and needs time to publish. The embargo is based on when the ephemeris was created
and which project created it, regardless of when observations were taken or pipeline runs executed.

Key scenarios tested:
1. Old observation + New ephemeris → ephemeris EMBARGOED
2. New observation + Old ephemeris → ephemeris PUBLIC
3. Embargoed ephemeris + ephemeris project member → can access
4. Embargoed ephemeris + non-member → cannot access, falls back to older non-embargoed
5. Superuser can access all embargoed ephemerides
6. Anonymous user can only access non-embargoed ephemerides
7. PTUSE project ephemerides are excluded
8. Pipeline runs without TOAs are skipped
"""

import json
import os
from datetime import datetime, timedelta

import pytz
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
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


class EphemerisEmbargoTestCase(GraphQLTestCase):
    """Test cases for ephemeris embargo logic based on ephemeris creation date"""

    RESIDUAL_EPHEMERIS_QUERY = """
    query {{
        pulsarFoldResult(
            pulsar: "{pulsar}",
            mainProject: "MeerTIME"
            first: 10
        ) {{
            residualEphemeris {{
                id
                ephemerisData
                createdAt
                dm
                p0
            }}
            residualEphemerisIsFromEmbargoedObservation
            residualEphemerisExistsButInaccessible
        }}
    }}
    """

    def setUp(self):
        """Setup test environment with users, projects, and base data."""
        # Create basic data
        self.telescope, _, self.ephemeris, self.template = create_basic_data()
        self.pulsar = Pulsar.objects.get(name="J0125-2327")

        # Use MeerTIME project
        main_project = MainProject.objects.get(name="MeerTIME")
        self.project = Project.objects.get(short="PTA", main_project=main_project)
        # Set a specific embargo period for consistent testing (18 months)
        self.project.embargo_period = timedelta(days=548)
        self.project.save()

        # Reassign ephemeris to the PTA project for testing
        self.ephemeris.project = self.project
        self.ephemeris.save()

        # Create a second project for cross-project testing
        self.project2 = Project.objects.create(
            main_project=main_project,
            code="TEST-PROJECT-2",
            short="TP2",
            embargo_period=timedelta(days=365),  # 12 months
        )

        # Create calibration
        self.calibration = Calibration.objects.create(
            schedule_block_id="test_sb_001",
            calibration_type="flux",
            location="/test/cal/location",
        )

        # Create users
        self.superuser = User.objects.create_superuser(
            username="superuser",
            email="super@test.com",
            password="testpass",
        )
        self.project_member = User.objects.create_user(
            username="project_member",
            email="member@test.com",
            password="testpass",
        )
        self.non_member = User.objects.create_user(
            username="non_member",
            email="nonmember@test.com",
            password="testpass",
        )

        # Create project membership
        ProjectMembership.objects.create(
            user=self.project_member,
            project=self.project,
            role=ProjectMembership.RoleChoices.MEMBER,
            is_active=True,
        )

    def _create_observation_with_pipeline_run(
        self,
        pulsar,
        project,
        ephemeris,
        observation_utc_start,
        ephemeris_created_at,
        create_toa=True,
    ):
        """
        Helper to create observation with pipeline run at specific dates.

        This allows testing the key distinction:
        - observation_utc_start: when the observation was taken (NOT used for embargo)
        - ephemeris_created_at: when the ephemeris was created (DETERMINES embargo)

        The ephemeris embargo is based on when the scientific model was created,
        not when observations were taken or pipeline runs were executed.
        """
        # Override the ephemeris created_at to our specific test date
        # This is what determines the embargo status
        Ephemeris.objects.filter(id=ephemeris.id).update(created_at=ephemeris_created_at)
        ephemeris.refresh_from_db()

        observation = Observation.objects.create(
            pulsar=pulsar,
            telescope=self.telescope,
            project=project,
            calibration=self.calibration,
            ephemeris=ephemeris,
            utc_start=observation_utc_start,
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

        # Create pipeline run (its created_at doesn't matter for embargo)
        pipeline_run = PipelineRun.objects.create(
            observation=observation,
            ephemeris=ephemeris,
            template=self.template,
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

        # Create PulsarFoldResult
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
                template=self.template,
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

    def test_old_observation_new_ephemeris_is_embargoed(self):
        """
        Test: Old observation (2020) with recent ephemeris (2025).
        Expected: Ephemeris should be embargoed based on ephemeris creation date.
        """
        self.client.force_login(self.non_member)
        now = timezone.now()

        # Observation from 2020 (old, would be public if we checked obs date)
        obs_date = datetime(2020, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        # Ephemeris created 1 month ago (recent, should be embargoed)
        ephemeris_date = now - timedelta(days=30)

        obs, pr = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=obs_date,
            ephemeris_created_at=ephemeris_date,
        )

        # Query as non-member
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Non-member should NOT see the embargoed ephemeris
        self.assertNotIn("errors", content)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNone(
            residual_eph,
            "Non-member should NOT see recently created embargoed ephemeris, " "even though observation is old",
        )

        # Check that existsButInaccessible is True (ephemerides exist but are inaccessible)
        exists_but_inaccessible = content["data"]["pulsarFoldResult"]["residualEphemerisExistsButInaccessible"]
        self.assertTrue(
            exists_but_inaccessible,
            "Should indicate that ephemerides exist but are inaccessible to non-member",
        )

    def test_new_observation_old_ephemeris_is_public(self):
        """
        Test: Recent observation (2025) with old ephemeris (2020).
        Expected: Ephemeris should be public based on old ephemeris creation date.
        """
        self.client.force_login(self.non_member)
        now = timezone.now()

        # Observation from 1 month ago (recent, would be embargoed if we checked obs date)
        obs_date = now - timedelta(days=30)
        # Ephemeris created in 2020 (old, should be public)
        ephemeris_date = datetime(2020, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)

        obs, pr = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=obs_date,
            ephemeris_created_at=ephemeris_date,
        )

        # Query as non-member
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Non-member SHOULD see the public ephemeris
        self.assertNotIn("errors", content)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Non-member SHOULD see old public ephemeris, " "even though observation is recent",
        )

        # Verify it's the correct ephemeris
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(str(self.ephemeris.id), decoded_eph_id)

        # Check that existsButInaccessible is None (accessible ephemeris found)
        exists_but_inaccessible = content["data"]["pulsarFoldResult"]["residualEphemerisExistsButInaccessible"]
        self.assertIsNone(
            exists_but_inaccessible,
            "Should be None when an accessible ephemeris is found",
        )

    def test_ephemeris_project_member_can_access_embargoed_ephemeris(self):
        """
        Test: Member of the ephemeris's project can access embargoed ephemeris.
        """
        self.client.force_login(self.project_member)
        now = timezone.now()

        # Recent ephemeris creation (embargoed)
        ephemeris_date = now - timedelta(days=30)
        obs_date = now - timedelta(days=30)

        obs, pr = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=obs_date,
            ephemeris_created_at=ephemeris_date,
        )

        # Query as project member (member of self.project, which is ephemeris.project)
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Project member SHOULD see the embargoed ephemeris
        self.assertNotIn("errors", content)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Ephemeris project member SHOULD see embargoed ephemeris from their project",
        )

        # Check the embargo flag is True
        is_embargoed = content["data"]["pulsarFoldResult"]["residualEphemerisIsFromEmbargoedObservation"]
        self.assertTrue(is_embargoed, "Should indicate the ephemeris is embargoed")

        # Check that existsButInaccessible is None (accessible ephemeris found)
        exists_but_inaccessible = content["data"]["pulsarFoldResult"]["residualEphemerisExistsButInaccessible"]
        self.assertIsNone(
            exists_but_inaccessible,
            "Should be None when project member has access to embargoed ephemeris",
        )

    def test_non_member_falls_back_to_older_non_embargoed_ephemeris(self):
        """
        Test: Non-member cannot access embargoed ephemeris but can access
        older non-embargoed ephemeris.
        """
        self.client.force_login(self.non_member)
        now = timezone.now()

        # Create different ephemerides
        with open(os.path.join(TEST_DATA_DIR, "J0125-2327.par"), "r") as par_file:
            par_text = par_file.read()
        ephemeris_dict = parse_ephemeris_file(par_text)

        # Embargoed ephemeris (recently created)
        embargoed_ephemeris = Ephemeris.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            ephemeris_data=json.dumps({"marker": "embargoed", **ephemeris_dict}),
            p0=ephemeris_dict["P0"],
            dm=ephemeris_dict["DM"],
            valid_from=ephemeris_dict["START"],
            valid_to=ephemeris_dict["FINISH"],
        )

        # Create pipeline run with recent ephemeris (embargoed) - most recent pipeline run
        recent_ephemeris_date = now - timedelta(days=30)
        obs1, pr1 = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            embargoed_ephemeris,
            observation_utc_start=now - timedelta(days=30),
            ephemeris_created_at=recent_ephemeris_date,
        )

        # Create pipeline run with old ephemeris (public) - older pipeline run
        old_ephemeris_date = now - timedelta(days=600)  # ~20 months ago, past embargo
        obs2, pr2 = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=now - timedelta(days=600),
            ephemeris_created_at=old_ephemeris_date,
        )

        # Query as non-member
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Non-member should see the older public ephemeris, not the embargoed one
        self.assertNotIn("errors", content)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Non-member should see the older public ephemeris",
        )

        # Verify it's the public ephemeris (self.ephemeris), not the embargoed one
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return the older public ephemeris, not the recently created embargoed one",
        )

        # Check the embargo flag is False
        is_embargoed = content["data"]["pulsarFoldResult"]["residualEphemerisIsFromEmbargoedObservation"]
        self.assertFalse(is_embargoed, "Should indicate the ephemeris is NOT embargoed")

        # Check that existsButInaccessible is None (accessible ephemeris found)
        exists_but_inaccessible = content["data"]["pulsarFoldResult"]["residualEphemerisExistsButInaccessible"]
        self.assertIsNone(
            exists_but_inaccessible,
            "Should be None when non-member falls back to older public ephemeris",
        )

    def test_superuser_can_access_all_embargoed_ephemerides(self):
        """
        Test: Superuser can access all ephemerides including embargoed ones.
        """
        self.client.force_login(self.superuser)
        now = timezone.now()

        # Recent ephemeris creation (embargoed)
        ephemeris_date = now - timedelta(days=30)

        obs, pr = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=now - timedelta(days=30),
            ephemeris_created_at=ephemeris_date,
        )

        # Query as superuser
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Superuser SHOULD see the embargoed ephemeris
        self.assertNotIn("errors", content)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Superuser SHOULD see embargoed ephemeris",
        )

    def test_ptuse_project_ephemerides_excluded(self):
        """
        Test: PTUSE project ephemerides are excluded from results.
        """
        self.client.force_login(self.non_member)
        now = timezone.now()

        # Create PTUSE project
        main_project = MainProject.objects.get(name="MeerTIME")
        ptuse_project = Project.objects.create(
            code="SCI-20180516-MB-PTUSE",
            short="PTUSE",
            main_project=main_project,
        )

        # Create PTUSE ephemeris (should be excluded)
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

        # Create observation with PTUSE ephemeris (should be excluded even though ephemeris is public)
        old_date = now - timedelta(days=600)
        obs_ptuse, pr_ptuse = self._create_observation_with_pipeline_run(
            self.pulsar,
            ptuse_project,
            ptuse_ephemeris,
            observation_utc_start=old_date,
            ephemeris_created_at=old_date,  # Old ephemeris (public)
        )

        # Create observation with regular (non-PTUSE) ephemeris
        obs_regular, pr_regular = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=old_date,
            ephemeris_created_at=old_date,
        )

        # Query
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should return the regular ephemeris, not PTUSE
        self.assertNotIn("errors", content)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(residual_eph)

        # Verify it's NOT the PTUSE ephemeris
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return regular ephemeris, not PTUSE",
        )

    def test_pipeline_runs_without_toas_are_skipped(self):
        """
        Test: Pipeline runs without TOAs are skipped.
        """
        self.client.force_login(self.non_member)
        now = timezone.now()
        old_date = now - timedelta(days=600)

        # Create different ephemerides
        with open(os.path.join(TEST_DATA_DIR, "J0125-2327.par"), "r") as par_file:
            par_text = par_file.read()
        ephemeris_dict = parse_ephemeris_file(par_text)

        no_toa_ephemeris = Ephemeris.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            ephemeris_data=json.dumps({"marker": "no_toa", **ephemeris_dict}),
            p0=ephemeris_dict["P0"],
            dm=ephemeris_dict["DM"],
            valid_from=ephemeris_dict["START"],
            valid_to=ephemeris_dict["FINISH"],
        )

        # Create pipeline run WITHOUT TOAs (should be skipped)
        obs_no_toa, pr_no_toa = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            no_toa_ephemeris,
            observation_utc_start=old_date,
            ephemeris_created_at=old_date,  # Old ephemeris (public)
            create_toa=False,  # No TOA
        )

        # Create pipeline run WITH TOAs
        obs_with_toa, pr_with_toa = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=old_date,
            ephemeris_created_at=old_date,
            create_toa=True,
        )

        # Query
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Should return the ephemeris with TOAs, not the one without
        self.assertNotIn("errors", content)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(residual_eph, "Should return ephemeris from pipeline run with TOAs")

        # Verify it's the ephemeris with TOAs
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return ephemeris with TOAs, not the one without",
        )

    def test_embargo_flag_reflects_ephemeris_embargo_status(self):
        """
        Test: The residualEphemerisIsFromEmbargoedObservation flag correctly reflects
        whether the ephemeris is embargoed (not the observation or pipeline run).
        """
        self.client.force_login(self.project_member)
        now = timezone.now()

        # Case 1: Recent observation, old ephemeris → flag should be False
        obs1, pr1 = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.ephemeris,
            observation_utc_start=now - timedelta(days=30),  # Recent obs
            ephemeris_created_at=now - timedelta(days=600),  # Old ephemeris
        )

        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        is_embargoed = content["data"]["pulsarFoldResult"]["residualEphemerisIsFromEmbargoedObservation"]
        self.assertFalse(
            is_embargoed,
            "Flag should be False for old ephemeris, even with recent observation",
        )
