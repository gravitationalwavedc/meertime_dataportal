"""
Test cases for multi-project ToA downloads
"""

import logging
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from dataportal.models import Observation, Project, ProjectMembership, Toa
from dataportal.tests.testing_utils import setup_query_test
from utils.constants import UserRole


class MultiProjectToaDownloadTestCase(TestCase):
    """Tests for multi-project ToA downloads"""

    def setUp(self):
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)

        # Create a temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        settings.MEERTIME_DATA_DIR = str(self.test_dir)

        # Set up test data using setup_query_test
        (
            _,
            self.unrestricted_user,
            self.telescope,
            self.project1,
            self.ephemeris,
            self.template,
            self.pipeline_run,
            self.observation,
            self.cal,
        ) = setup_query_test()

        # Use the observation's actual project as project1
        # (setup_query_test may return different project than observation belongs to)
        self.project1 = self.observation.project

        # Ensure the main_project is named "MeerTime" for filtering tests
        if self.project1.main_project:
            self.project1.main_project.name = "MeerTime"
            self.project1.main_project.save()

        # Ensure the user has unrestricted role for testing
        self.unrestricted_user.role = UserRole.UNRESTRICTED.value
        self.unrestricted_user.save()

        # Create additional projects for multi-project testing
        # These need to have the same main_project to pass observation filtering
        self.project2 = Project.objects.create(
            main_project=self.project1.main_project,
            code="SCI-20180516-MB-03",
            short="TPA2",
            embargo_period=timedelta(days=548),
        )

        self.project3 = Project.objects.create(
            main_project=self.project1.main_project,
            code="SCI-20180516-MB-06",
            short="COWD",
            embargo_period=timedelta(days=548),
        )

        # Create a restricted user for testing permissions
        self.restricted_user = get_user_model().objects.create_user(
            username="restricted", email="restricted@example.com", password="secret", role=UserRole.RESTRICTED.value
        )

        # Create a user who is member of only project1
        self.project1_member = get_user_model().objects.create_user(
            username="project1_member", email="p1@example.com", password="secret", role=UserRole.RESTRICTED.value
        )
        ProjectMembership.objects.create(
            user=self.project1_member,
            project=self.project1,
            role=ProjectMembership.RoleChoices.MEMBER,
            is_active=True,
        )

        # Create a user who is member of project1 and project2
        self.multi_project_member = get_user_model().objects.create_user(
            username="multi_member", email="multi@example.com", password="secret", role=UserRole.RESTRICTED.value
        )
        ProjectMembership.objects.create(
            user=self.multi_project_member,
            project=self.project1,
            role=ProjectMembership.RoleChoices.MEMBER,
            is_active=True,
        )
        ProjectMembership.objects.create(
            user=self.multi_project_member,
            project=self.project2,
            role=ProjectMembership.RoleChoices.MEMBER,
            is_active=True,
        )

        # Create a superuser
        self.superuser = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="admin"
        )

    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)
        shutil.rmtree(self.test_dir)

    def _create_toa_file(self, observation, project):
        """Helper to create a ToA file on disk and in database"""
        obs_dir = (
            self.test_dir
            / observation.pulsar.name
            / observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(observation.beam)
            / "timing"
            / project.short
        )
        obs_dir.mkdir(parents=True, exist_ok=True)
        toas_file = (
            obs_dir
            / f"{observation.pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )
        toas_file.write_text(f"ToAs content for {project.short}")

        # Create Toa model instance
        Toa.objects.create(
            pipeline_run=self.pipeline_run,
            observation=observation,
            project=project,
            ephemeris=self.ephemeris,
            template=self.template,
            archive=toas_file.name,
            freq_MHz=1400.0,
            mjd=59000.0,
            mjd_err=0.001,
            telescope="Murriyang",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            obs_npol=1,
        )

        return toas_file

    def test_download_toas_from_multiple_projects_unrestricted(self):
        """Unrestricted user gets ToAs from all projects"""
        # Create ToA files for all three projects
        self._create_toa_file(self.observation, self.project1)
        self._create_toa_file(self.observation, self.project2)
        self._create_toa_file(self.observation, self.project3)

        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        # Check zip contains files from all projects
        content = b"".join(response.streaming_content)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            with zipfile.ZipFile(tmp_file_path, "r") as zf:
                members = zf.namelist()
                # Should have 3 ToA files (one per project)
                self.assertEqual(len(members), 3)
                # Check all projects are represented
                self.assertTrue(any(self.project1.short in m for m in members))
                self.assertTrue(any(self.project2.short in m for m in members))
                self.assertTrue(any(self.project3.short in m for m in members))
        finally:
            Path(tmp_file_path).unlink()

    @freeze_time("1990-01-01")
    def test_download_toas_user_member_of_subset(self):
        """User who is member of 2/3 projects gets only those 2 ToAs"""
        # Create ToA files for all three projects
        self._create_toa_file(self.observation, self.project1)
        self._create_toa_file(self.observation, self.project2)
        self._create_toa_file(self.observation, self.project3)

        self.client.force_login(self.multi_project_member)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        # Check zip contains files only from accessible projects
        content = b"".join(response.streaming_content)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            with zipfile.ZipFile(tmp_file_path, "r") as zf:
                members = zf.namelist()
                # Should have 2 ToA files (member of project1 and project2)
                self.assertEqual(len(members), 2)
                # Check correct projects are represented
                self.assertTrue(any(self.project1.short in m for m in members))
                self.assertTrue(any(self.project2.short in m for m in members))
                # Should NOT have project3
                self.assertFalse(any(self.project3.short in m for m in members))
        finally:
            Path(tmp_file_path).unlink()

    @freeze_time("1990-01-01")
    def test_download_toas_embargoed_with_membership(self):
        """User with project membership can access embargoed multi-project ToAs"""
        # Create ToA files for project1 only
        self._create_toa_file(self.observation, self.project1)

        self.client.force_login(self.project1_member)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)

    @freeze_time("1990-01-01")
    def test_download_toas_embargoed_no_membership(self):
        """User without observation project membership gets 403 (Gate 1)"""
        # Create ToA files for all projects
        self._create_toa_file(self.observation, self.project1)
        self._create_toa_file(self.observation, self.project2)

        self.client.force_login(self.restricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        # Gate 1: observation is embargoed and restricted_user is not in observation's project
        # Should return 403 regardless of ToA projects existing
        self.assertEqual(response.status_code, 403)
        self.assertIn("Access denied", response.content.decode())

    @freeze_time("1990-01-01")
    def test_download_toas_superuser_gets_all(self):
        """Superuser gets all ToAs regardless of embargo or membership"""
        # Create ToA files for all three projects
        self._create_toa_file(self.observation, self.project1)
        self._create_toa_file(self.observation, self.project2)
        self._create_toa_file(self.observation, self.project3)

        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        self.assertEqual(response.status_code, 200)

        # Check zip contains files from all projects
        content = b"".join(response.streaming_content)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            with zipfile.ZipFile(tmp_file_path, "r") as zf:
                members = zf.namelist()
                self.assertEqual(len(members), 3)
                # All projects should be present
                self.assertTrue(any(self.project1.short in m for m in members))
                self.assertTrue(any(self.project2.short in m for m in members))
                self.assertTrue(any(self.project3.short in m for m in members))
        finally:
            Path(tmp_file_path).unlink()

    def test_download_toas_no_toas_in_database(self):
        """Returns 404 when no ToAs exist in database (Gate 2)"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        # Gate 2: No accessible ToAs, should return 404
        self.assertEqual(response.status_code, 404)
        self.assertIn("No ToA files are available", response.content.decode())

    @freeze_time("1990-01-01")
    def test_download_toas_inactive_membership_denied(self):
        """User with inactive membership cannot access embargoed ToAs (Gate 1)"""
        # Create ToA file for project1
        self._create_toa_file(self.observation, self.project1)

        # Set membership to inactive
        membership = ProjectMembership.objects.get(user=self.project1_member, project=self.project1)
        membership.is_active = False
        membership.save()

        self.client.force_login(self.project1_member)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        # Gate 1: observation is embargoed and user has inactive membership (not in project)
        # Should return 403
        self.assertEqual(response.status_code, 403)
        self.assertIn("Access denied", response.content.decode())

    def test_download_pulsar_toas_multi_observation_multi_project(self):
        """Pulsar-level download includes all accessible ToAs from multiple observations and projects"""
        # Create second observation
        obs2 = Observation.objects.create(
            pulsar=self.observation.pulsar,
            telescope=self.telescope,
            project=self.project1,
            calibration=self.cal,
            band=self.observation.band,
            frequency=self.observation.frequency,
            bandwidth=self.observation.bandwidth,
            nchan=self.observation.nchan,
            beam=self.observation.beam,
            nant=self.observation.nant,
            nant_eff=self.observation.nant_eff,
            npol=self.observation.npol,
            obs_type="fold",
            utc_start=self.observation.utc_start + timedelta(days=1),
            raj=self.observation.raj,
            decj=self.observation.decj,
            duration=3600.0,
            nbit=self.observation.nbit,
            tsamp=self.observation.tsamp,
            fold_nbin=1024,
            fold_nchan=1024,
            fold_tsubint=10.0,
        )

        # Create ToA files for both observations, multiple projects each
        self._create_toa_file(self.observation, self.project1)
        self._create_toa_file(self.observation, self.project2)
        self._create_toa_file(obs2, self.project1)
        self._create_toa_file(obs2, self.project3)

        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "toas"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        # Check zip contains files from all observations and projects
        content = b"".join(response.streaming_content)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            with zipfile.ZipFile(tmp_file_path, "r") as zf:
                members = zf.namelist()
                # Should have 4 ToA files (2 observations x varying projects)
                self.assertEqual(len(members), 4)
                # Check nested structure: timing/{timestamp}/{beam}/timing/{project}/{filename}
                obs1_timestamp = self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                obs2_timestamp = obs2.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                # Verify timestamps and projects are in paths
                self.assertTrue(any(obs1_timestamp in m and self.project1.short in m for m in members))
                self.assertTrue(any(obs1_timestamp in m and self.project2.short in m for m in members))
                self.assertTrue(any(obs2_timestamp in m and self.project1.short in m for m in members))
                self.assertTrue(any(obs2_timestamp in m and self.project3.short in m for m in members))
        finally:
            Path(tmp_file_path).unlink()

    def test_no_toas_returns_404(self):
        """When no ToAs exist, observation download returns 404 (Gate 2 blocks)"""
        # Don't create any ToAs
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "toas",
                },
            )
        )

        # Gate 2: No accessible ToAs → 404
        self.assertEqual(response.status_code, 404)
        self.assertIn("No ToA files are available", response.content.decode())

    def test_download_pulsar_toas_excludes_molonglo(self):
        """Verify Molonglo observations are excluded from pulsar-level ToA downloads"""
        # Create a Molonglo main project and telescope
        molonglo_telescope = self.telescope  # reuse existing telescope
        molonglo_main_project = self.observation.project.main_project  # Get existing main_project

        # Change the main_project name to create distinction
        meertime_main_project = molonglo_main_project
        meertime_main_project.name = "MeerTime"
        meertime_main_project.save()

        # Create a separate Molonglo main project
        molonglo_main_project = self.observation.project.main_project.__class__.objects.create(
            telescope=molonglo_telescope, name="Molonglo"
        )

        # Create a Molonglo project
        molonglo_project = Project.objects.create(
            main_project=molonglo_main_project,
            code="MOLONGLO-01",
            short="MOL",
            embargo_period=timedelta(days=0),  # No embargo for simplicity
        )

        # Create a Molonglo observation for the same pulsar
        molonglo_obs = Observation.objects.create(
            pulsar=self.observation.pulsar,
            telescope=molonglo_telescope,
            project=molonglo_project,
            calibration=self.cal,  # Add calibration to avoid signal handler error
            band=self.observation.band,
            frequency=self.observation.frequency,
            bandwidth=self.observation.bandwidth,
            nchan=self.observation.nchan,
            beam=self.observation.beam,
            nant=self.observation.nant,
            nant_eff=self.observation.nant_eff,
            npol=self.observation.npol,
            obs_type="fold",
            utc_start=datetime(2023, 11, 1, 10, 0, 0, tzinfo=pytz.UTC),
            raj=self.observation.raj,
            decj=self.observation.decj,
            duration=self.observation.duration,
            nbit=self.observation.nbit,
            tsamp=self.observation.tsamp,
            fold_nbin=self.observation.fold_nbin,
            fold_nchan=self.observation.fold_nchan,
            fold_tsubint=self.observation.fold_tsubint,
        )

        # Ensure the MeerTime observation's project has the MeerTime main_project
        self.observation.project.main_project = meertime_main_project
        self.observation.project.save()

        # Create ToA files for both observations
        self._create_toa_file(self.observation, self.project1)  # MeerTime
        self._create_toa_file(molonglo_obs, molonglo_project)  # Molonglo

        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "toas"})
        )

        self.assertEqual(response.status_code, 200)

        # Check that only MeerTime observation is included
        content = b"".join(response.streaming_content)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            with zipfile.ZipFile(tmp_file_path, "r") as zf:
                members = zf.namelist()
                # Should have only 1 file (MeerTime observation)
                self.assertEqual(len(members), 1)
                # Verify it's the MeerTime observation, not Molonglo
                meertime_timestamp = self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                molonglo_timestamp = molonglo_obs.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                self.assertTrue(any(meertime_timestamp in m for m in members))
                self.assertFalse(any(molonglo_timestamp in m for m in members))
        finally:
            Path(tmp_file_path).unlink()

    def test_download_pulsar_toas_excludes_search_observations(self):
        """Verify search-type observations are excluded from pulsar-level ToA downloads"""
        # Ensure the observation's project has MeerTime main_project
        meertime_main_project = self.observation.project.main_project
        meertime_main_project.name = "MeerTime"
        meertime_main_project.save()

        # Create a search observation for the same pulsar
        search_obs = Observation.objects.create(
            pulsar=self.observation.pulsar,
            telescope=self.telescope,
            project=self.project1,  # Same project, different obs_type
            calibration=self.cal,  # Add calibration to avoid signal handler error
            band=self.observation.band,
            frequency=self.observation.frequency,
            bandwidth=self.observation.bandwidth,
            nchan=self.observation.nchan,
            beam=self.observation.beam,
            nant=self.observation.nant,
            nant_eff=self.observation.nant_eff,
            npol=self.observation.npol,
            obs_type="search",  # Search observation
            utc_start=datetime(2023, 11, 1, 10, 0, 0, tzinfo=pytz.UTC),
            raj=self.observation.raj,
            decj=self.observation.decj,
            duration=self.observation.duration,
            nbit=self.observation.nbit,
            tsamp=self.observation.tsamp,
            filterbank_nbit=8,
            filterbank_npol=1,
            filterbank_nchan=32,
            filterbank_tsamp=64.0,
            filterbank_dm=0.0,
        )

        # Create ToA files for both observations
        self._create_toa_file(self.observation, self.project1)  # Fold observation
        self._create_toa_file(search_obs, self.project1)  # Search observation

        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "toas"})
        )

        self.assertEqual(response.status_code, 200)

        # Check that only fold observation is included
        content = b"".join(response.streaming_content)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            with zipfile.ZipFile(tmp_file_path, "r") as zf:
                members = zf.namelist()
                # Should have only 1 file (fold observation)
                self.assertEqual(len(members), 1)
                # Verify it's the fold observation, not search
                fold_timestamp = self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                search_timestamp = search_obs.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                self.assertTrue(any(fold_timestamp in m for m in members))
                self.assertFalse(any(search_timestamp in m for m in members))
        finally:
            Path(tmp_file_path).unlink()
