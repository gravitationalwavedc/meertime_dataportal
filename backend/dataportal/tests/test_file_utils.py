from pathlib import Path
from unittest import mock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponse, FileResponse

from utils.constants import UserRole
from dataportal.file_utils import get_file_list, get_file_path, serve_file


class FileUtilsTestCase(TestCase):
    """Tests for file utility functions"""

    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="testuser", email="test@example.com", password="secret", role=UserRole.UNRESTRICTED.value
        )
        # Create a restricted user for testing permissions
        self.restricted_user = self.User.objects.create_user(
            username="restricted", email="restricted@example.com", password="secret", role=UserRole.RESTRICTED.value
        )

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


class FileDownloadViewTestCase(TestCase):
    """Tests for file download view"""

    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        # Create an unrestricted user
        self.unrestricted_user = self.User.objects.create_user(
            username="unrestricted",
            email="unrestricted@example.com",
            password="secret",
            role=UserRole.UNRESTRICTED.value,
        )
        # Create a restricted user
        self.restricted_user = self.User.objects.create_user(
            username="restricted", email="restricted@example.com", password="secret", role=UserRole.RESTRICTED.value
        )
        # Create an admin user
        self.admin_user = self.User.objects.create_user(
            username="admin", email="admin@example.com", password="secret", role=UserRole.ADMIN.value
        )

    @override_settings(MEERTIME_DATA_DIR="/mnt/meertime_data")
    @mock.patch("dataportal.views.serve_file")
    def test_download_file_view_unrestricted(self, mock_serve_file):
        """Test download_file view when authenticated as an unrestricted user"""
        # Setup mock to return a proper HttpResponse
        test_content = b"Test file content"
        mock_response = HttpResponse(content=test_content, content_type="application/octet-stream")
        mock_response["Content-Disposition"] = 'attachment; filename="myfile.txt"'
        mock_serve_file.return_value = mock_response

        # Login the unrestricted user
        self.client.login(username="unrestricted", password="secret")

        # Call the view
        response = self.client.get(reverse("download_file", kwargs={"file_path": "test/myfile.txt"}))

        # Check response
        mock_serve_file.assert_called_once_with("test/myfile.txt")
        self.assertEqual(response.content, test_content)

    @override_settings(MEERTIME_DATA_DIR="/mnt/meertime_data")
    @mock.patch("dataportal.views.serve_file")
    def test_download_file_view_admin(self, mock_serve_file):
        """Test download_file view when authenticated as an admin user"""
        # Setup a proper HTTP response mock with the necessary headers
        test_content = b"Test file content"
        http_response = HttpResponse(test_content)
        mock_serve_file.return_value = http_response

        # Login the admin user
        self.client.login(username="admin", password="secret")

        # Call the view
        response = self.client.get(reverse("download_file", kwargs={"file_path": "test/myfile.txt"}))

        # Check response
        mock_serve_file.assert_called_once_with("test/myfile.txt")
        self.assertEqual(response.content, test_content)

    @override_settings(MEERTIME_DATA_DIR="/mnt/meertime_data")
    def test_download_file_view_restricted(self):
        """Test download_file view when authenticated as restricted user"""
        # Login the restricted user
        self.client.login(username="restricted", password="secret")

        # Call the view
        response = self.client.get(reverse("download_file", kwargs={"file_path": "test/myfile.txt"}))

        # Check response is forbidden
        self.assertEqual(response.status_code, 403)

    @override_settings(MEERTIME_DATA_DIR="/mnt/meertime_data")
    def test_download_file_view_unauthenticated(self):
        """Test download_file view when not authenticated"""
        # Call the view without logging in
        response = self.client.get(reverse("download_file", kwargs={"file_path": "test/myfile.txt"}))

        # Check response is unauthorized
        self.assertEqual(response.status_code, 401)
