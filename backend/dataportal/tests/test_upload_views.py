import json
import os
from unittest import mock
from io import BytesIO

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from utils.constants import UserRole
from dataportal.models import Project, Pulsar, PipelineRun, PulsarFoldResult, Template, PipelineImage
from dataportal.tests.testing_utils import create_basic_data, create_observation_pipeline_run_toa

User = get_user_model()


class UploadTemplateViewTestCase(TestCase):
    """Tests for UploadTemplate ViewSet permissions"""

    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

        # Create users with different roles
        self.unrestricted_user = self.User.objects.create_user(
            username="unrestricted",
            email="unrestricted@example.com",
            password="secret",
            role=UserRole.UNRESTRICTED.value,
        )
        self.restricted_user = self.User.objects.create_user(
            username="restricted", email="restricted@example.com", password="secret", role=UserRole.RESTRICTED.value
        )
        self.admin_user = self.User.objects.create_user(
            username="admin", email="admin@example.com", password="secret", role=UserRole.ADMIN.value
        )

        # Create basic test data
        telescope, project, ephemeris, template = create_basic_data()
        self.project = project
        self.pulsar = template.pulsar

        # Create a mock template file
        self.template_file = SimpleUploadedFile(
            "test_template.par", b"Test template content", content_type="text/plain"
        )

    def test_upload_template_unrestricted_user_with_permission(self):
        """Test template upload with unrestricted user (has add_template permission)"""
        # Grant the specific permission to unrestricted user
        content_type = ContentType.objects.get_for_model(Template)
        permission = Permission.objects.get(
            codename="add_template",
            content_type=content_type,
        )
        self.unrestricted_user.user_permissions.add(permission)

        self.client.login(username="unrestricted@example.com", password="secret")

        response = self.client.post(
            reverse("upload_template-list"),
            {
                "template_upload": self.template_file,
                "pulsar_name": self.pulsar.name,
                "project_code": self.project.code,
                "band": "LBAND",
            },
        )

        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["success"])

    def test_upload_template_restricted_user_without_permission(self):
        """Test template upload with restricted user (no add_template permission)"""
        self.client.login(username="restricted@example.com", password="secret")

        response = self.client.post(
            reverse("upload_template-list"),
            {
                "template_upload": self.template_file,
                "pulsar_name": self.pulsar.name,
                "project_code": self.project.code,
                "band": "LBAND",
            },
        )

        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.content)
        self.assertIn("detail", response_data)  # DRF uses "detail" for error messages

    def test_upload_template_unauthenticated(self):
        """Test template upload without authentication"""
        response = self.client.post(
            reverse("upload_template-list"),
            {
                "template_upload": self.template_file,
                "pulsar_name": self.pulsar.name,
                "project_code": self.project.code,
                "band": "LBAND",
            },
        )

        # Note: DRF permission classes return 403 for both unauthenticated and unauthorized users
        # when accessed through ViewSets
        self.assertEqual(response.status_code, 403)


class UploadPipelineImageViewTestCase(TestCase):
    """Tests for UploadPipelineImage ViewSet permissions"""

    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

        # Create users with different roles
        self.unrestricted_user = self.User.objects.create_user(
            username="unrestricted",
            email="unrestricted@example.com",
            password="secret",
            role=UserRole.UNRESTRICTED.value,
        )
        self.restricted_user = self.User.objects.create_user(
            username="restricted", email="restricted@example.com", password="secret", role=UserRole.RESTRICTED.value
        )
        self.admin_user = self.User.objects.create_user(
            username="admin", email="admin@example.com", password="secret", role=UserRole.ADMIN.value
        )

        # Create basic test data
        telescope, project, ephemeris, template = create_basic_data()
        observation, pulsar_fold_result, pipeline_run = create_observation_pipeline_run_toa(
            os.path.join(os.path.dirname(__file__), "test_data", "2023-04-17-15:08:35_1_J0437-4715.json"),
            telescope,
            template,
            make_toas=False,
        )
        self.pipeline_run = pipeline_run

        # Create a mock image file
        self.image_file = SimpleUploadedFile("test_image.png", b"fake image content", content_type="image/png")

    def test_upload_pipeline_image_unrestricted_user_with_permission(self):
        """Test pipeline image upload with unrestricted user (has add_pipelineimage permission)"""
        # Grant the specific permission to unrestricted user
        content_type = ContentType.objects.get_for_model(PipelineImage)
        permission = Permission.objects.get(
            codename="add_pipelineimage",
            content_type=content_type,
        )
        self.unrestricted_user.user_permissions.add(permission)

        self.client.login(username="unrestricted@example.com", password="secret")

        response = self.client.post(
            reverse("upload_image-list"),
            {
                "pipeline_run_id": self.pipeline_run.id,
                "image_upload": self.image_file,
                "image_type": "profile",
                "resolution": "high",
                "cleaned": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["success"])

    def test_upload_pipeline_image_restricted_user_without_permission(self):
        """Test pipeline image upload with restricted user (no add_pipelineimage permission)"""
        self.client.login(username="restricted@example.com", password="secret")

        response = self.client.post(
            reverse("upload_image-list"),
            {
                "pipeline_run_id": self.pipeline_run.id,
                "image_upload": self.image_file,
                "image_type": "profile",
                "resolution": "high",
                "cleaned": True,
            },
        )

        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.content)
        self.assertIn("detail", response_data)  # DRF uses "detail" for error messages

    def test_upload_pipeline_image_unauthenticated(self):
        """Test pipeline image upload without authentication"""
        response = self.client.post(
            reverse("upload_image-list"),
            {
                "pipeline_run_id": self.pipeline_run.id,
                "image_upload": self.image_file,
                "image_type": "profile",
                "resolution": "high",
                "cleaned": True,
            },
        )

        # Note: DRF permission classes return 403 for both unauthenticated and unauthorized users
        # when accessed through ViewSets
        self.assertEqual(response.status_code, 403)
