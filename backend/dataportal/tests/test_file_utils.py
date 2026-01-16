import logging
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from freezegun import freeze_time

from dataportal.file_utils import get_file_list, get_file_path, serve_file
from dataportal.models import Observation, PipelineRun, ProjectMembership, Toa
from dataportal.tests.testing_utils import setup_query_test
from utils.constants import UserRole


class FileUtilsTestCase(TestCase):
    """Tests for file utility functions"""

    def setUp(self):
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)

        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="secret", role=UserRole.UNRESTRICTED.value
        )
        # Create a restricted user for testing permissions
        self.restricted_user = self.User.objects.create_user(
            username="restricted", email="restricted@example.com", password="secret", role=UserRole.RESTRICTED.value
        )

        # Create a temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        settings.MEERTIME_DATA_DIR = str(self.test_dir)

        # Create some test files and directories
        (self.test_dir / "test_dir").mkdir()
        (self.test_dir / "test_dir" / "test_file.txt").write_text("test content")

    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)
        shutil.rmtree(self.test_dir)

    @override_settings(MEERTIME_DATA_DIR="/mnt/meertime_data")
    def test_get_file_list(self):
        """Test get_file_list function"""
        # Create mock Path objects for the iterator
        file1_mock = mock.MagicMock()
        file1_mock.name = "file1.ar"
        file1_mock.is_file.return_value = True
        file1_mock.is_dir.return_value = False
        file1_mock.relative_to.return_value = mock.MagicMock()  # Mock the return value instead of using Path
        file1_mock.relative_to.return_value.as_posix.return_value = "file1.ar"

        file2_mock = mock.MagicMock()
        file2_mock.name = "file2.ar"
        file2_mock.is_file.return_value = True
        file2_mock.is_dir.return_value = False
        file2_mock.relative_to.return_value = mock.MagicMock()
        file2_mock.relative_to.return_value.as_posix.return_value = "file2.ar"

        subdir_mock = mock.MagicMock()
        subdir_mock.name = "subdir"
        subdir_mock.is_file.return_value = False
        subdir_mock.is_dir.return_value = True
        subdir_mock.relative_to.return_value = mock.MagicMock()
        subdir_mock.relative_to.return_value.as_posix.return_value = "subdir"

        # Set up stat mock for file size
        stat_result = mock.MagicMock()
        stat_result.st_size = 1024

        # Mock the entire file_utils.Path to avoid the _flavour issue
        with mock.patch("dataportal.file_utils.Path") as mock_path_class:
            # Configure the Path mock to return our mock instance
            path_instance = mock.MagicMock()
            path_instance.exists.return_value = True
            path_instance.is_dir.return_value = True
            path_instance.iterdir.return_value = [file1_mock, file2_mock, subdir_mock]

            # Configure the division operator (/) to return the path instance itself for chaining
            path_instance.__truediv__.return_value = path_instance
            mock_path_class.return_value = path_instance

            # Configure stat for all files
            path_instance.stat.return_value = stat_result
            file1_mock.stat.return_value = stat_result
            file2_mock.stat.return_value = stat_result
            subdir_mock.stat.return_value = stat_result

            # Call the function we're testing
            success, result = get_file_list("/test/path", False)

        # Check results
        self.assertTrue(success)
        self.assertEqual(len(result), 3)

        # Verify each item has the expected properties
        for item in result:
            self.assertIn("path", item)
            self.assertIn("fileName", item)
            self.assertIn("fileSize", item)
            self.assertIn("isDirectory", item)

    @override_settings(MEERTIME_DATA_DIR="/mnt/meertime_data")
    @mock.patch("dataportal.file_utils.get_file_path")
    @mock.patch("pathlib.Path.open")
    def test_serve_file(self, mock_open, mock_get_file_path):
        """Test serve_file function"""
        # Setup mocks
        mock_get_file_path.return_value = (True, Path("/mnt/meertime_data/test/myfile.txt"))
        mock_open.return_value = mock.MagicMock()

        # Call the function
        response = serve_file("/test/myfile.txt")

        # Check response
        self.assertIsNotNone(response)
        mock_get_file_path.assert_called_once_with("/test/myfile.txt")
        mock_open.assert_called_once_with("rb")

    def test_get_file_list_nonexistent(self):
        """Test getting a list of files from a nonexistent directory"""
        success, result = get_file_list("nonexistent")
        self.assertFalse(success)
        self.assertEqual(result, "Path not found: nonexistent")

    def test_get_file_list_not_directory(self):
        """Test getting a list of files from a path that is not a directory"""
        # Create a file in the root directory
        (self.test_dir / "test_file.txt").write_text("test content")

        success, result = get_file_list("test_file.txt")
        self.assertFalse(success)
        self.assertEqual(result, "Path is not a directory: test_file.txt")

    def test_get_file_list_recursive(self):
        """Test getting a recursive list of files"""
        # Create a nested directory structure
        nested_dir = self.test_dir / "test_dir" / "nested_dir"
        nested_dir.mkdir(parents=True)
        (nested_dir / "nested_file.txt").write_text("nested content")

        success, result = get_file_list("test_dir", recursive=True)
        self.assertTrue(success)
        self.assertEqual(len(result), 2)  # Should find both files
        file_names = [item["fileName"] for item in result]
        self.assertIn("test_file.txt", file_names)
        self.assertIn("nested_file.txt", file_names)

    def test_get_file_path(self):
        """Test getting a file path"""
        success, result = get_file_path("test_dir/test_file.txt")
        self.assertTrue(success)
        self.assertEqual(result.name, "test_file.txt")

    def test_get_file_path_nonexistent(self):
        """Test getting a nonexistent file path"""
        success, result = get_file_path("nonexistent.txt")
        self.assertFalse(success)
        self.assertEqual(result, "File not found: nonexistent.txt")

    def test_serve_file_nonexistent(self):
        """Test serving a nonexistent file"""
        response = serve_file("nonexistent.txt")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), "File not found: nonexistent.txt")


class DownloadViewsTestCase(TestCase):
    """Tests for the download views"""

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
            self.project,
            self.ephemeris,
            self.template,
            self.pipeline_run,
            self.observation,
            self.cal,
        ) = setup_query_test()

        # Ensure the project's main_project is named "MeerTime" for filtering
        if self.project.main_project:
            self.project.main_project.name = "MeerTime"
            self.project.main_project.save()

        # Ensure the user has unrestricted role for testing
        self.unrestricted_user.role = UserRole.UNRESTRICTED.value
        self.unrestricted_user.save()

        # Create a restricted user for testing permissions
        self.restricted_user = get_user_model().objects.create_user(
            username="restricted", email="restricted@example.com", password="secret", role=UserRole.RESTRICTED.value
        )

        # Create test files
        obs_dir = (
            self.test_dir
            / self.observation.pulsar.name
            / self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(self.observation.beam)
        )
        obs_dir.mkdir(parents=True)
        (obs_dir / "decimated").mkdir()

        self.full_res_file = (
            obs_dir
            / f"{self.observation.pulsar.name}_{self.observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap.ar"
        )
        self.decimated_file = (
            obs_dir
            / "decimated"
            / f"{self.observation.pulsar.name}_{self.observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.1ch_1p_1t.ar"
        )

        self.full_res_file.write_text("full resolution content")
        self.decimated_file.write_text("decimated content")

    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)
        shutil.rmtree(self.test_dir)

    def test_download_observation_files_unauthorized(self):
        """Test downloading observation files without authentication"""
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "full",
                },
            )
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content.decode(), "Unauthorized - please log in")

    def test_download_observation_files_full(self):
        """Test downloading full resolution observation file"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "full",
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        # Read the file content from the response
        expected_content = self.full_res_file.read_text()
        self.assertEqual(response.streaming_content.__next__().decode(), expected_content)

    def test_download_observation_files_decimated(self):
        """Test downloading decimated observation file"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "decimated",
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        # Read the file content from the response
        expected_content = self.decimated_file.read_text()
        self.assertEqual(response.streaming_content.__next__().decode(), expected_content)

    def test_download_observation_files_invalid_type(self):
        """Test downloading observation file with invalid type"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "invalid",
                },
            )
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid file type specified")

    def test_download_observation_files_not_found(self):
        """Test downloading non-existent observation file"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": "NONEXISTENT",
                    "observation_timestamp": "2023-01-01-00:00:00",
                    "beam": 1,
                    "file_type": "full",
                },
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), "Observation not found")

    @freeze_time("1990-01-01")
    def test_download_observation_files_restricted(self):
        """Test downloading restricted observation file"""
        # Use freezegun to set current time to 1990, making the embargo date
        # (utc_start + project.embargo_period) be in the future
        self.client.force_login(self.restricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "full",
                },
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(), "Access denied - data is under embargo. Please request to join project."
        )

    @freeze_time("1990-01-01")
    def test_download_observation_files_project_member_access(self):
        """Test that project members can access embargoed observation files from their project"""
        # Create a project member for this observation's project
        # Note: self.observation.project may differ from self.project (depends on JSON test data)
        project_member = get_user_model().objects.create_user(
            username="project_member", email="member@example.com", password="secret"
        )
        ProjectMembership.objects.create(
            user=project_member,
            project=self.observation.project,
            role=ProjectMembership.RoleChoices.MEMBER,
        )

        # Use freezegun to set current time to 1990, making the embargo date
        # (utc_start + project.embargo_period) be in the future (embargoed)
        # But project members should still be able to access their project's data
        self.client.force_login(project_member)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "full",
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        # Read the file content from the response
        expected_content = self.full_res_file.read_text()
        self.assertEqual(response.streaming_content.__next__().decode(), expected_content)

    @freeze_time("1990-01-01")
    def test_download_observation_files_superuser_access(self):
        """Test that superusers can access all embargoed observation files"""
        # Create a superuser
        superuser = get_user_model().objects.create_user(
            username="superuser", email="super@example.com", password="secret", is_superuser=True
        )

        # Use freezegun to set current time to 1990, making the embargo date
        # (utc_start + project.embargo_period) be in the future (embargoed)
        # Superusers should be able to access any data
        self.client.force_login(superuser)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "full",
                },
            )
        )
        self.assertEqual(response.status_code, 200)
        # Read the file content from the response
        expected_content = self.full_res_file.read_text()
        self.assertEqual(response.streaming_content.__next__().decode(), expected_content)

    @freeze_time("1990-01-01")
    def test_download_observation_files_non_member_denied(self):
        """Test that non-project-members cannot access embargoed observation files"""
        # Use freezegun to set current time to 1990, making the embargo date
        # (utc_start + project.embargo_period) be in the future (embargoed)
        # Non-members (unrestricted_user is not a project member) should be denied
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": self.observation.pulsar.name,
                    "observation_timestamp": self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    "beam": self.observation.beam,
                    "file_type": "full",
                },
            )
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(), "Access denied - data is under embargo. Please request to join project."
        )

    def test_download_pulsar_files_unauthorized(self):
        """Test downloading pulsar files without authentication"""
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "full"})
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content.decode(), "Unauthorized - please log in")

    def test_download_pulsar_files_full(self):
        """Test downloading full resolution pulsar files"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "full"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(
            response["Content-Disposition"],
            f'attachment; filename="pulsar_{self.observation.pulsar.name}_full_files.zip"',
        )
        # Check that the zip file contains our test files
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)  # Zip file should not be empty

    def test_download_pulsar_files_decimated(self):
        """Test downloading decimated pulsar files"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "decimated"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(
            response["Content-Disposition"],
            f'attachment; filename="pulsar_{self.observation.pulsar.name}_decimated_files.zip"',
        )
        # Check that the zip file contains our test files
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)  # Zip file should not be empty

    def test_download_pulsar_files_invalid_type(self):
        """Test downloading pulsar files with invalid file type"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "invalid"})
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid file type specified")

    def test_download_pulsar_files_not_found(self):
        """Test downloading non-existent pulsar files"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": "NONEXISTENT", "file_type": "full"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), "Pulsar not found")

    @freeze_time("1990-01-01")
    def test_download_pulsar_files_restricted(self):
        """Test downloading pulsar files with restricted observations"""
        # Use freezegun to set current time to 1990, making all embargo dates
        # (utc_start + project.embargo_period) be in the future
        self.client.force_login(self.restricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "full"})
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(), "Access denied - all data is under embargo. Please request to join project(s)."
        )

    @freeze_time("1990-01-01")
    def test_download_pulsar_files_mixed_access(self):
        """Test downloading pulsar files with a mix of restricted and unrestricted observations"""
        # Create a second observation that will be unrestricted (embargo in the past)
        unrestricted_obs = Observation.objects.create(
            pulsar=self.observation.pulsar,
            telescope=self.telescope,
            project=self.project,
            calibration=self.cal,
            band=self.observation.band,
            frequency=self.observation.frequency,
            bandwidth=self.observation.bandwidth,
            nchan=self.observation.nchan,
            beam=self.observation.beam,
            nant=self.observation.nant,
            nant_eff=self.observation.nant_eff,
            npol=self.observation.npol,
            obs_type="fold",  # Set to fold type
            utc_start=self.observation.utc_start + timedelta(days=1),  # Different time
            raj=self.observation.raj,
            decj=self.observation.decj,
            duration=3600.0,  # 1 hour duration
            nbit=self.observation.nbit,
            tsamp=self.observation.tsamp,
            # Add fold-specific fields
            fold_nbin=1024,
            fold_nchan=1024,
            fold_tsubint=10.0,  # 10 second sub-integrations
        )

        # Now set the embargo dates after creation to avoid save() method overwriting them
        # Set the first observation to be restricted (future embargo)
        Observation.objects.filter(id=self.observation.id).update(
            embargo_end_date=datetime.now(tz=pytz.UTC) + timedelta(days=1)
        )
        # Set the second observation to be unrestricted (past embargo)
        Observation.objects.filter(id=unrestricted_obs.id).update(
            embargo_end_date=datetime.now(tz=pytz.UTC) - timedelta(days=1)
        )

        # Create test files for the unrestricted observation
        obs_dir = (
            self.test_dir
            / unrestricted_obs.pulsar.name
            / unrestricted_obs.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(unrestricted_obs.beam)
        )
        obs_dir.mkdir(parents=True)
        (obs_dir / "decimated").mkdir()

        unrestricted_full_res = (
            obs_dir
            / f"{unrestricted_obs.pulsar.name}_{unrestricted_obs.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap.ar"
        )
        unrestricted_decimated = (
            obs_dir
            / "decimated"
            / f"{unrestricted_obs.pulsar.name}_{unrestricted_obs.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.1ch_1p_1t.ar"
        )

        unrestricted_full_res.write_text("unrestricted full resolution content")
        unrestricted_decimated.write_text("unrestricted decimated content")

        self.client.force_login(self.restricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "full"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        # Create a temporary directory to extract the zip file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write the zip file content to a temporary file
            zip_path = Path(temp_dir) / "test.zip"
            with open(zip_path, "wb") as f:
                for chunk in response.streaming_content:
                    f.write(chunk)

            # Extract the zip file
            with zipfile.ZipFile(zip_path, "r") as zip:
                members = zip.namelist()
                # Should only contain files from the unrestricted observation
                self.assertEqual(len(members), 1)  # One full resolution file

                # Check for the new structure: timestamp/beam/filename
                timestamp_dir = unrestricted_obs.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                beam_dir = str(unrestricted_obs.beam)
                full_filename = (
                    f"{unrestricted_obs.pulsar.name}_{unrestricted_obs.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap.ar"
                )

                expected_full_path = f"{timestamp_dir}/{beam_dir}/{full_filename}"

                self.assertIn(expected_full_path, members)

    @freeze_time("1990-01-01")
    def test_download_pulsar_files_project_member_access(self):
        """Test that project members can access embargoed pulsar files from their project"""
        # Create a project member for this observation's project
        # Note: self.observation.project may differ from self.project (depends on JSON test data)
        project_member = get_user_model().objects.create_user(
            username="project_member", email="member@example.com", password="secret"
        )
        ProjectMembership.objects.create(
            user=project_member,
            project=self.observation.project,
            role=ProjectMembership.RoleChoices.MEMBER,
        )

        # Use freezegun to set current time to 1990, making the embargo date
        # (utc_start + project.embargo_period) be in the future (embargoed)
        # But project members should still be able to access their project's data
        self.client.force_login(project_member)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "full"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(
            response["Content-Disposition"],
            f'attachment; filename="pulsar_{self.observation.pulsar.name}_full_files.zip"',
        )
        # Check that the zip file contains our test files
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)  # Zip file should not be empty

    @freeze_time("1990-01-01")
    def test_download_pulsar_files_superuser_access(self):
        """Test that superusers can access all embargoed pulsar files"""
        # Create a superuser
        superuser = get_user_model().objects.create_user(
            username="superuser", email="super@example.com", password="secret", is_superuser=True
        )

        # Use freezegun to set current time to 1990, making the embargo date
        # (utc_start + project.embargo_period) be in the future (embargoed)
        # Superusers should be able to access any data
        self.client.force_login(superuser)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "full"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(
            response["Content-Disposition"],
            f'attachment; filename="pulsar_{self.observation.pulsar.name}_full_files.zip"',
        )
        # Check that the zip file contains our test files
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)  # Zip file should not be empty

    @freeze_time("1990-01-01")
    def test_download_pulsar_files_non_member_denied(self):
        """Test that non-project-members cannot access embargoed pulsar files"""
        # Use freezegun to set current time to 1990, making the embargo date
        # (utc_start + project.embargo_period) be in the future (embargoed)
        # Non-members (unrestricted_user is not a project member) should be denied
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "full"})
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(), "Access denied - all data is under embargo. Please request to join project(s)."
        )

    def test_download_observation_files_toas_unauthorized(self):
        """Test downloading ToAs file without authentication"""
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
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content.decode(), "Unauthorized - please log in")

    def test_download_observation_files_toas(self):
        """Test downloading ToAs file for a specific observation"""
        # Import Toa model for creating test data

        # Create the ToAs file with project folder
        obs_dir = (
            self.test_dir
            / self.observation.pulsar.name
            / self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(self.observation.beam)
            / "timing"
            / self.project.short  # Add project folder
        )
        obs_dir.mkdir(parents=True)
        toas_file = (
            obs_dir
            / f"{self.observation.pulsar.name}_{self.observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )
        toas_file.write_text("ToAs content")

        # Create Toa model instance so database query finds it
        Toa.objects.create(
            pipeline_run=self.pipeline_run,
            observation=self.observation,
            project=self.project,
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
        # Check that we get a zip file
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)

    def test_download_observation_files_toas_not_found(self):
        """Test downloading non-existent observation ToAs file"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse(
                "download_observation_files",
                kwargs={
                    "jname": "NONEXISTENT",
                    "observation_timestamp": "2023-01-01-00:00:00",
                    "beam": 1,
                    "file_type": "toas",
                },
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), "Observation not found")

    @freeze_time("1990-01-01")
    def test_download_observation_files_toas_restricted(self):
        """Test downloading restricted observation ToAs file - should return 403 (Gate 1)"""
        # Create the ToAs file with project folder
        obs_dir = (
            self.test_dir
            / self.observation.pulsar.name
            / self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(self.observation.beam)
            / "timing"
            / self.project.short  # Add project folder
        )
        obs_dir.mkdir(parents=True)
        toas_file = (
            obs_dir
            / f"{self.observation.pulsar.name}_{self.observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )
        toas_file.write_text("ToAs content")

        # Create Toa model instance
        Toa.objects.create(
            pipeline_run=self.pipeline_run,
            observation=self.observation,
            project=self.project,
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
        # Gate 1: observation is embargoed and user is not in observation's project
        # Should return 403 regardless of ToA projects
        self.assertEqual(response.status_code, 403)
        self.assertIn("Access denied", response.content.decode())

    def test_download_pulsar_files_toas_unauthorized(self):
        """Test downloading pulsar ToAs files without authentication"""
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "toas"})
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content.decode(), "Unauthorized - please log in")

    def test_download_pulsar_files_toas(self):
        """Test downloading all ToAs files for a pulsar"""
        # Import Toa model for creating test data

        # Create the ToAs file with project folder
        obs_dir = (
            self.test_dir
            / self.observation.pulsar.name
            / self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(self.observation.beam)
            / "timing"
            / self.project.short  # Add project folder
        )
        obs_dir.mkdir(parents=True)
        toas_file = (
            obs_dir
            / f"{self.observation.pulsar.name}_{self.observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )
        toas_file.write_text("ToAs content")

        # Create Toa model instance
        Toa.objects.create(
            pipeline_run=self.pipeline_run,
            observation=self.observation,
            project=self.project,
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

        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "toas"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(
            response["Content-Disposition"],
            f'attachment; filename="pulsar_{self.observation.pulsar.name}_toas_files.zip"',
        )
        # Check that the zip file contains our test files
        content = b"".join(response.streaming_content)
        self.assertGreater(len(content), 0)  # Zip file should not be empty

    def test_download_pulsar_files_toas_not_found(self):
        """Test downloading non-existent pulsar ToAs files"""
        self.client.force_login(self.unrestricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": "NONEXISTENT", "file_type": "toas"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), "Pulsar not found")

    @freeze_time("1990-01-01")
    def test_download_pulsar_files_toas_restricted(self):
        """Test downloading pulsar ToAs files with restricted observations - returns empty zip with README"""
        # Import Toa model for creating test data

        # Create the ToAs file with project folder
        obs_dir = (
            self.test_dir
            / self.observation.pulsar.name
            / self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(self.observation.beam)
            / "timing"
            / self.project.short  # Add project folder
        )
        obs_dir.mkdir(parents=True)
        toas_file = (
            obs_dir
            / f"{self.observation.pulsar.name}_{self.observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )
        toas_file.write_text("ToAs content")

        # Create Toa model instance
        Toa.objects.create(
            pipeline_run=self.pipeline_run,
            observation=self.observation,
            project=self.project,
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

        self.client.force_login(self.restricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "toas"})
        )
        # With new behavior, embargo check happens before generate_zip
        # If all observations are restricted, returns 403
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(), "Access denied - all data is under embargo. Please request to join project(s)."
        )

    @freeze_time("1990-01-01")
    def test_download_pulsar_files_toas_mixed_access(self):
        """Test downloading pulsar ToAs files with mixed access (restricted and unrestricted)"""
        # Create a second observation that will be unrestricted
        # Use utc_start from 1988 so embargo ends before frozen time (1990)
        unrestricted_obs = Observation.objects.create(
            pulsar=self.observation.pulsar,
            telescope=self.telescope,
            project=self.project,
            calibration=self.cal,
            band=self.observation.band,
            frequency=self.observation.frequency,
            bandwidth=self.observation.bandwidth,
            nchan=self.observation.nchan,
            beam=self.observation.beam,
            nant=self.observation.nant,
            nant_eff=self.observation.nant_eff,
            npol=self.observation.npol,
            obs_type="fold",  # Set to fold type
            utc_start=datetime(1988, 1, 1, tzinfo=pytz.UTC),  # 1988 + 548 days = ~1989-07, before 1990
            raj=self.observation.raj,
            decj=self.observation.decj,
            duration=3600.0,  # 1 hour duration
            nbit=self.observation.nbit,
            tsamp=self.observation.tsamp,
            # Add fold-specific fields
            fold_nbin=1024,
            fold_nchan=1024,
            fold_tsubint=10.0,  # 10 second sub-integrations
        )

        # Now set the embargo dates after creation to avoid save() method overwriting them
        # Set the first observation to be restricted (future embargo)
        Observation.objects.filter(id=self.observation.id).update(
            embargo_end_date=datetime.now(tz=pytz.UTC) + timedelta(days=1)
        )
        # Set the second observation to be unrestricted (past embargo)
        Observation.objects.filter(id=unrestricted_obs.id).update(
            embargo_end_date=datetime.now(tz=pytz.UTC) - timedelta(days=1)
        )

        # Create ToAs files for both observations with project folder
        # Import Toa model

        obs_dir = (
            self.test_dir
            / self.observation.pulsar.name
            / self.observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(self.observation.beam)
            / "timing"
            / self.project.short  # Add project folder
        )
        obs_dir.mkdir(parents=True)
        restricted_toas = (
            obs_dir
            / f"{self.observation.pulsar.name}_{self.observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )
        restricted_toas.write_text("Restricted ToAs content")

        # Create Toa model instance for restricted observation
        Toa.objects.create(
            pipeline_run=self.pipeline_run,
            observation=self.observation,
            project=self.project,
            ephemeris=self.ephemeris,
            template=self.template,
            archive=restricted_toas.name,
            freq_MHz=1400.0,
            mjd=59000.0,
            mjd_err=0.001,
            telescope="Murriyang",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            obs_npol=1,
        )

        unrestricted_obs_dir = (
            self.test_dir
            / unrestricted_obs.pulsar.name
            / unrestricted_obs.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(unrestricted_obs.beam)
            / "timing"
            / self.project.short  # Add project folder
        )
        unrestricted_obs_dir.mkdir(parents=True)
        unrestricted_toas = (
            unrestricted_obs_dir
            / f"{unrestricted_obs.pulsar.name}_{unrestricted_obs.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )
        unrestricted_toas.write_text("Unrestricted ToAs content")

        # Create Toa model instance for unrestricted observation
        # Need to create a pipeline run for the unrestricted observation first
        unrestricted_pipeline_run = PipelineRun.objects.create(
            observation=unrestricted_obs,
            ephemeris=self.ephemeris,
            template=self.template,
        )
        Toa.objects.create(
            pipeline_run=unrestricted_pipeline_run,
            observation=unrestricted_obs,
            project=self.project,
            ephemeris=self.ephemeris,
            template=self.template,
            archive=unrestricted_toas.name,
            freq_MHz=1400.0,
            mjd=59000.0,
            mjd_err=0.001,
            telescope="Murriyang",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            obs_npol=1,
        )

        self.client.force_login(self.restricted_user)
        response = self.client.get(
            reverse("download_pulsar_files", kwargs={"jname": self.observation.pulsar.name, "file_type": "toas"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

        # Create a temporary directory to extract the zip file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write the zip file content to a temporary file
            zip_path = Path(temp_dir) / "test.zip"
            with open(zip_path, "wb") as f:
                for chunk in response.streaming_content:
                    f.write(chunk)

            # Extract the zip file
            with zipfile.ZipFile(zip_path, "r") as zip:
                members = zip.namelist()
                # Should only contain files from the unrestricted observation
                self.assertEqual(len(members), 1)  # One ToAs file

                # Check for the expected structure: timing/timestamp/beam/timing/project/filename
                timestamp_dir = unrestricted_obs.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                beam_dir = str(unrestricted_obs.beam)
                toas_filename = f"{unrestricted_obs.pulsar.name}_{unrestricted_obs.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"

                expected_toas_path = f"timing/{timestamp_dir}/{beam_dir}/timing/{self.project.short}/{toas_filename}"

                self.assertIn(expected_toas_path, members)
