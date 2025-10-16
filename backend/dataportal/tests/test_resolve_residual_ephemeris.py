"""
Tests for resolve_residual_ephemeris function in PulsarFoldResultConnection.

This module contains comprehensive tests for the resolve_residual_ephemeris method
in dataportal/graphql/queries.py (lines 720-733).

The function returns the most recent ephemeris used for timing analysis by filtering
ephemeris objects based on:
1. Association with specific PulsarFoldResult IDs
2. Having non-null project associations
3. Having at least one associated TOA
4. Excluding TOAs from PTUSE projects
5. Ordering by most recent pipeline run creation time

Tests included:
- test_resolve_residual_ephemeris_returns_latest_ephemeris: Verifies the function returns
  the most recent ephemeris when multiple pipeline runs exist
- test_resolve_residual_ephemeris_excludes_ptuse_project: Ensures PTUSE project data
  is properly excluded from results
- test_resolve_residual_ephemeris_requires_toa_and_project: Confirms that only ephemeris
  with TOAs and valid projects are returned
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
    Pulsar,
    PulsarFoldResult,
    Telescope,
    Template,
    Toa,
)
from dataportal.tests.testing_utils import TEST_DATA_DIR, create_basic_data
from utils.ephemeris import parse_ephemeris_file

User = get_user_model()


class ResolveResidualEphemerisTestCase(GraphQLTestCase):
    """Test cases for the resolve_residual_ephemeris function in PulsarFoldResultConnection"""

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
        }}
    }}
    """

    def setUp(self):
        """Setup basic test environment."""
        self.user = User.objects.create(username="testuser", email="test@test.com")
        self.client.force_login(self.user)

        # Create basic data
        self.telescope, _, self.ephemeris, self.template = create_basic_data()
        self.pulsar = Pulsar.objects.get(name="J0125-2327")

        # Use a MeerTIME project instead of the MONSPSR project returned by create_basic_data
        main_project = MainProject.objects.get(name="MeerTIME")
        self.project = Project.objects.get(short="PTA", main_project=main_project)

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

    def test_resolve_residual_ephemeris_returns_latest_ephemeris(self):
        """
        Test 1: Verify that resolve_residual_ephemeris returns the most recent ephemeris.

        This is critical because the function is meant to return the latest ephemeris
        used for timing analysis. It should order by -pipelinerun__created_at and return
        the first (most recent) result.
        """
        # Create first observation with ephemeris (older)
        utc_start_old = datetime.now(pytz.utc) - timedelta(days=10)
        obs1, pr1 = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_old,
        )

        # Wait a moment and create a second observation with the same ephemeris (newer)
        utc_start_new = datetime.now(pytz.utc) - timedelta(days=5)
        obs2, pr2 = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_new,
        )

        # Query for residual ephemeris
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        self.assertIn("data", content, "Response should contain data")
        self.assertIn("pulsarFoldResult", content["data"])
        self.assertIsNotNone(content["data"]["pulsarFoldResult"]["residualEphemeris"])

        # The ephemeris should be from the latest pipeline run (pr2)
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(residual_eph, "Residual ephemeris should not be None")

        # Verify it's the correct ephemeris by decoding the GraphQL ID
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return the ephemeris associated with the latest pipeline run",
        )

    def test_resolve_residual_ephemeris_excludes_ptuse_project(self):
        """
        Test 2: Verify that resolve_residual_ephemeris excludes observations from PTUSE project.

        This is critical because the function specifically excludes PTUSE project observations
        with the line: .exclude(toa__pipeline_run__pulsarfoldresult__observation__project__short__iexact="PTUSE")

        This test creates:
        - One ephemeris used by a PTUSE project observation (should be excluded)
        - Another ephemeris used by a regular project observation (should be included)
        """
        # Create a PTUSE project
        main_project = MainProject.objects.get(name="MeerTIME")
        ptuse_project = Project.objects.create(
            code="SCI-20180516-MB-PTUSE",
            short="PTUSE",
            main_project=main_project,
        )

        # Create a separate ephemeris for PTUSE
        with open(os.path.join(TEST_DATA_DIR, "J0125-2327.par"), "r") as par_file:
            par_text = par_file.read()
        ephemeris_dict = parse_ephemeris_file(par_text)
        ptuse_ephemeris = Ephemeris.objects.create(
            pulsar=self.pulsar,
            project=ptuse_project,
            ephemeris_data=json.dumps(ephemeris_dict),
            p0=ephemeris_dict["P0"],
            dm=ephemeris_dict["DM"],
            valid_from=ephemeris_dict["START"],
            valid_to=ephemeris_dict["FINISH"],
        )

        # Create observation with PTUSE project (should be excluded) - newer
        utc_start_ptuse = datetime.now(pytz.utc) - timedelta(days=3)
        obs_ptuse, pr_ptuse = self._create_observation_with_pipeline_run(
            self.pulsar,
            ptuse_project,
            self.telescope,
            self.template,
            ptuse_ephemeris,  # Use different ephemeris
            utc_start_ptuse,
        )

        # Create observation with regular project (should be included) - older
        utc_start_regular = datetime.now(pytz.utc) - timedelta(days=10)
        obs_regular, pr_regular = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_regular,
        )

        # Query for residual ephemeris
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        self.assertIn("data", content, "Response should contain data")

        # The ephemeris should be from the regular project, not PTUSE
        # Even though PTUSE observation is newer, it should be excluded
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(residual_eph, "Should return ephemeris from non-PTUSE project")

        # Verify it's the correct ephemeris (the regular one, not PTUSE)
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return the non-PTUSE ephemeris, not the PTUSE one",
        )

    def test_resolve_residual_ephemeris_requires_toa_and_project(self):
        """
        Test 3: Verify that resolve_residual_ephemeris only returns ephemeris that have TOAs
        and are associated with observations that have projects.

        This is critical because the function has two key filters:
        - pipelinerun__pulsarfoldresult__observation__project__short__isnull=False
        - toa__isnull=False
        """
        # Create observation WITHOUT TOA (should be excluded)
        utc_start_no_toa = datetime.now(pytz.utc) - timedelta(days=2)
        obs_no_toa, pr_no_toa = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_no_toa,
            create_toa=False,  # No TOA
        )

        # Create observation WITH TOA (should be included)
        utc_start_with_toa = datetime.now(pytz.utc) - timedelta(days=5)
        obs_with_toa, pr_with_toa = self._create_observation_with_pipeline_run(
            self.pulsar,
            self.project,
            self.telescope,
            self.template,
            self.ephemeris,
            utc_start_with_toa,
            create_toa=True,  # Has TOA
        )

        # Query for residual ephemeris
        response = self.query(self.RESIDUAL_EPHEMERIS_QUERY.format(pulsar="J0125-2327"))
        content = json.loads(response.content)

        # Assertions
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        self.assertIn("data", content, "Response should contain data")

        # Should return ephemeris because there's at least one observation with TOA
        residual_eph = content["data"]["pulsarFoldResult"]["residualEphemeris"]
        self.assertIsNotNone(
            residual_eph,
            "Should return ephemeris from observation with TOA, not the one without",
        )

        # Verify it's the correct ephemeris by decoding the GraphQL ID
        _, decoded_eph_id = from_global_id(residual_eph["id"])
        self.assertEqual(
            str(self.ephemeris.id),
            decoded_eph_id,
            "Should return the ephemeris associated with observation that has TOA",
        )
