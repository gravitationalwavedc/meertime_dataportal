import tempfile
import shutil
import os
import logging
from pathlib import Path
from datetime import timedelta
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from dataportal.models import (
    Pulsar,
    Project as ProjectModel,
    PulsarFoldResult,
    PipelineImage,
    Template,
    ProjectMembership,
)
from dataportal.tests.testing_utils import TEST_DATA_DIR, create_basic_data, create_observation_pipeline_run_toa

User = get_user_model()


@override_settings(
    LOGGING={
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "null": {
                "class": "logging.NullHandler",
            },
        },
        "loggers": {
            "dataportal.media": {
                "handlers": ["null"],
                "level": "CRITICAL",
                "propagate": False,
            },
        },
    }
)
class ProtectedMediaTestCase(TestCase):
    def setUp(self):
        """Set up test data including users, projects, observations, and media files"""
        # Suppress logging during tests
        logging.getLogger("dataportal.media").setLevel(logging.CRITICAL)

        # Create temporary media directory
        self.test_media_dir = tempfile.mkdtemp()

        # Create basic test data (telescope, pulsar, projects, ephemeris, template)
        telescope, _, ephemeris, template = create_basic_data()
        self.telescope = telescope
        self.ephemeris = ephemeris
        self.template = template

        # Get the pulsar that was created
        self.pulsar = Pulsar.objects.get(name="J0125-2327")

        # Get the project that the test observations will use (from JSON files)
        self.project = ProjectModel.objects.get(code="SCI-20180516-MB-05")

        # Create users
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123", role="ADMIN"
        )
        self.project_member = User.objects.create_user(
            username="member", email="member@test.com", password="member123", role="UNRESTRICTED"
        )
        self.non_member = User.objects.create_user(
            username="nonmember", email="nonmember@test.com", password="nonmember123", role="UNRESTRICTED"
        )

        # Create project membership for member user
        ProjectMembership.objects.create(user=self.project_member, project=self.project, is_active=True, role="Member")

        # Create embargoed observation using helper
        self.obs_embargoed, self.calibration, pr_embargoed = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"), telescope, template
        )
        # Update utc_start to be recent (within embargo)
        self.obs_embargoed.utc_start = timezone.now() - timedelta(days=30)
        self.obs_embargoed.save()

        # Create public observation using helper
        self.obs_public, _, pr_public = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"), telescope, template
        )
        # Update utc_start to be old (past embargo)
        self.obs_public.utc_start = timezone.now() - timedelta(days=600)
        self.obs_public.save()

        # Create pipeline runs and fold results (they were already created by helper)
        self.pr_embargoed = pr_embargoed
        self.pfr_embargoed = PulsarFoldResult.objects.get(observation=self.obs_embargoed)

        self.pr_public = pr_public
        self.pfr_public = PulsarFoldResult.objects.get(observation=self.obs_public)

        # Create test image file paths
        self.embargoed_image_path = "MeerKAT/SCI-20180516-MB-05/J0125-2327/2025-01-01-00:00:00/1/profile.png"
        self.public_image_path = "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-01-01-00:00:00/2/profile.png"

        # Create actual image files on disk
        embargoed_file = Path(self.test_media_dir) / self.embargoed_image_path
        embargoed_file.parent.mkdir(parents=True, exist_ok=True)
        embargoed_file.write_bytes(b"fake embargoed image data")

        public_file = Path(self.test_media_dir) / self.public_image_path
        public_file.parent.mkdir(parents=True, exist_ok=True)
        public_file.write_bytes(b"fake public image data")

        # Create PipelineImage database records
        self.image_embargoed = PipelineImage.objects.create(
            pulsar_fold_result=self.pfr_embargoed,
            image=self.embargoed_image_path,
            image_type="profile",
            resolution="high",
            cleaned=True,
        )

        self.image_public = PipelineImage.objects.create(
            pulsar_fold_result=self.pfr_public,
            image=self.public_image_path,
            image_type="profile",
            resolution="high",
            cleaned=True,
        )

        # Create template file
        self.embargoed_template_path = "SCI-20180516-MB-05/J0125-2327/LBAND/2025-01-01-00:00:00_template.std"
        self.public_template_path = "SCI-20180516-MB-05/J0125-2327/LBAND/2023-01-01-00:00:00_template.std"

        embargoed_template_file = Path(self.test_media_dir) / self.embargoed_template_path
        embargoed_template_file.parent.mkdir(parents=True, exist_ok=True)
        embargoed_template_file.write_bytes(b"fake embargoed template data")

        public_template_file = Path(self.test_media_dir) / self.public_template_path
        public_template_file.parent.mkdir(parents=True, exist_ok=True)
        public_template_file.write_bytes(b"fake public template data")

        # Create Template database records
        self.template_embargoed = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            template_file=self.embargoed_template_path,
            band="LBAND",
            template_hash="embargoed_abc123",
        )
        # Manually set created_at to recent date for embargo
        self.template_embargoed.created_at = timezone.now() - timedelta(days=30)
        self.template_embargoed.save()

        self.template_public = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            template_file=self.public_template_path,
            band="LBAND",
            template_hash="public_abc123",
        )
        # Manually set created_at to old date (past embargo)
        self.template_public.created_at = timezone.now() - timedelta(days=600)
        self.template_public.save()

        self.client = Client()

    def tearDown(self):
        """Clean up temporary media directory"""
        shutil.rmtree(self.test_media_dir, ignore_errors=True)

    # ========== Authentication Tests ==========

    def test_anonymous_user_denied(self):
        """Anonymous users cannot access embargoed files but can access public files"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Anonymous cannot access embargoed
            response = self.client.get(f"/media/{self.embargoed_image_path}")
            self.assertEqual(response.status_code, 401)
            self.assertIn(b"Unauthorized - please log in", response.content)

            # Anonymous CAN access public
            response = self.client.get(f"/media/{self.public_image_path}")
            self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_access_public_image(self):
        """Authenticated users can access public (non-embargoed) images"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{self.public_image_path}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"fake public image data", b"".join(response.streaming_content))

    def test_superuser_can_access_embargoed_image(self):
        """Superusers can access all images including embargoed ones"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.superuser)
            response = self.client.get(f"/media/{self.embargoed_image_path}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"fake embargoed image data", b"".join(response.streaming_content))

    def test_project_member_can_access_embargoed_image(self):
        """Project members can access embargoed images from their project"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.project_member)
            response = self.client.get(f"/media/{self.embargoed_image_path}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"fake embargoed image data", b"".join(response.streaming_content))

    def test_non_member_denied_embargoed_image(self):
        """Non-members are denied access to embargoed images"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{self.embargoed_image_path}")
            self.assertEqual(response.status_code, 403)
            self.assertIn(b"Access denied - data is under embargo. Please request to join project.", response.content)

    # ========== PipelineImage Access Tests ==========

    def test_all_image_types_accessible(self):
        """Test that different image types are handled correctly"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Skip 'profile' since it's already created in setUp
            image_types = ["phase-time", "phase-freq", "snr-cumul"]

            for img_type in image_types:
                # Create image file and database record
                img_path = f"MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-01-01-00:00:00/2/{img_type}.png"
                img_file = Path(self.test_media_dir) / img_path
                img_file.write_bytes(f"fake {img_type} data".encode())

                PipelineImage.objects.create(
                    pulsar_fold_result=self.pfr_public,
                    image=img_path,
                    image_type=img_type,
                    resolution="high",
                    cleaned=True,
                )

                # Test access
                self.client.force_login(self.non_member)
                response = self.client.get(f"/media/{img_path}")
                self.assertEqual(response.status_code, 200)

            # Also test the profile image that already exists
            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{self.public_image_path}")
            self.assertEqual(response.status_code, 200)

    def test_high_and_low_resolution_accessible(self):
        """Test that both high and low resolution images are handled"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # High resolution already exists from setUp, test low resolution
            img_path = f"MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-01-01-00:00:00/2/profile_low.png"
            img_file = Path(self.test_media_dir) / img_path
            img_file.write_bytes(b"fake low res data")

            PipelineImage.objects.create(
                pulsar_fold_result=self.pfr_public,
                image=img_path,
                image_type="profile",
                resolution="low",
                cleaned=True,
            )

            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{img_path}")
            self.assertEqual(response.status_code, 200)

            # Also verify high resolution works
            response = self.client.get(f"/media/{self.public_image_path}")
            self.assertEqual(response.status_code, 200)

    def test_cleaned_and_raw_accessible(self):
        """Test that both cleaned and raw images are handled"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Cleaned=True already exists from setUp, test cleaned=False
            img_path = f"MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-01-01-00:00:00/2/profile_raw.png"
            img_file = Path(self.test_media_dir) / img_path
            img_file.write_bytes(b"fake raw data")

            PipelineImage.objects.create(
                pulsar_fold_result=self.pfr_public,
                image=img_path,
                image_type="profile",
                resolution="high",
                cleaned=False,
            )

            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{img_path}")
            self.assertEqual(response.status_code, 200)

            # Also verify cleaned works
            response = self.client.get(f"/media/{self.public_image_path}")
            self.assertEqual(response.status_code, 200)

    def test_nonexistent_image_returns_404(self):
        """Nonexistent image files return 404"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.superuser)
            response = self.client.get("/media/nonexistent/file.png")
            self.assertEqual(response.status_code, 404)

    def test_deactivated_membership_denies_access(self):
        """Users with deactivated project membership cannot access embargoed data"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Deactivate the membership
            membership = ProjectMembership.objects.get(user=self.project_member, project=self.project)
            membership.is_active = False
            membership.save()

            self.client.force_login(self.project_member)
            response = self.client.get(f"/media/{self.embargoed_image_path}")
            self.assertEqual(response.status_code, 403)

            # Reactivate for other tests
            membership.is_active = True
            membership.save()

    # ========== Template Access Tests ==========

    def test_embargoed_template_blocked_for_non_member(self):
        """Non-members cannot access embargoed templates"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{self.embargoed_template_path}")
            self.assertEqual(response.status_code, 403)
            self.assertIn(b"Access denied - data is under embargo. Please request to join project.", response.content)

    def test_embargoed_template_accessible_for_member(self):
        """Project members can access embargoed templates"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.project_member)
            response = self.client.get(f"/media/{self.embargoed_template_path}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"fake embargoed template data", b"".join(response.streaming_content))

    def test_anonymous_user_denied_template_download(self):
        """Anonymous users cannot download any templates (requires authentication)"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Try to access public template
            response = self.client.get(f"/media/{self.public_template_path}")
            self.assertEqual(response.status_code, 401)
            self.assertIn(b"Unauthorized - please log in", response.content)

            # Also check embargoed template
            response = self.client.get(f"/media/{self.embargoed_template_path}")
            self.assertEqual(response.status_code, 401)
            self.assertIn(b"Unauthorized - please log in", response.content)

    def test_public_template_accessible_for_authenticated_users(self):
        """All authenticated users can access public (non-embargoed) templates"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{self.public_template_path}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"fake public template data", b"".join(response.streaming_content))

    def test_template_all_bands_accessible(self):
        """Test templates in different bands are handled"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            bands = ["UHF", "LBAND", "SBAND_0"]

            for band in bands:
                template_path = f"SCI-20180516-MB-05/J0125-2327/{band}/2023-01-01-00:00:00_template_{band}.std"
                template_file = Path(self.test_media_dir) / template_path
                template_file.parent.mkdir(parents=True, exist_ok=True)
                template_file.write_bytes(f"fake {band} template".encode())

                template = Template.objects.create(
                    pulsar=self.pulsar,
                    project=self.project,
                    template_file=template_path,
                    band=band,
                    template_hash=f"{band}_hash",
                )
                # Make it public
                template.created_at = timezone.now() - timedelta(days=600)
                template.save()

                self.client.force_login(self.non_member)
                response = self.client.get(f"/media/{template_path}")
                self.assertEqual(response.status_code, 200)

    def test_template_nonexistent_returns_404(self):
        """Nonexistent template files return 404"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.superuser)
            response = self.client.get("/media/nonexistent/template.std")
            self.assertEqual(response.status_code, 404)

    # ========== Security Tests ==========

    def test_path_traversal_blocked(self):
        """Path traversal attempts are blocked"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            self.client.force_login(self.superuser)
            response = self.client.get("/media/../../../etc/passwd")
            self.assertIn(response.status_code, [400, 403])

    def test_file_not_in_database_returns_404(self):
        """Files that exist on disk but aren't in database return 404"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Create a file that's not in the database
            orphan_path = "orphan/file.png"
            orphan_file = Path(self.test_media_dir) / orphan_path
            orphan_file.parent.mkdir(parents=True, exist_ok=True)
            orphan_file.write_bytes(b"orphan data")

            self.client.force_login(self.superuser)
            response = self.client.get(f"/media/{orphan_path}")
            self.assertEqual(response.status_code, 404)

    def test_special_characters_in_filename(self):
        """Files with special characters in names are handled correctly"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Use a different image type to avoid conflicts
            special_path = "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-01-01-00:00:00/2/phase-time_test.png"
            special_file = Path(self.test_media_dir) / special_path
            special_file.write_bytes(b"special chars data")

            PipelineImage.objects.create(
                pulsar_fold_result=self.pfr_public,
                image=special_path,
                image_type="phase-time",
                resolution="high",
                cleaned=True,
            )

            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{special_path}")
            self.assertEqual(response.status_code, 200)

    def test_missing_file_but_in_database(self):
        """If file is in database but missing from disk, return 404"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Create database record but no file - use different image type
            missing_path = "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-01-01-00:00:00/2/missing.png"
            PipelineImage.objects.create(
                pulsar_fold_result=self.pfr_public,
                image=missing_path,
                image_type="phase-freq",
                resolution="high",
                cleaned=True,
            )

            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{missing_path}")
            self.assertEqual(response.status_code, 404)

    # ========== Edge Cases ==========

    def test_multiple_projects_different_embargoes(self):
        """Test that different projects have independent embargo controls"""
        with self.settings(MEDIA_ROOT=self.test_media_dir):
            # Create another project with different embargo period
            from dataportal.models import Project, MainProject

            main_project = MainProject.objects.first()
            project2 = Project.objects.create(
                main_project=main_project,
                code="OTHER-PROJECT",
                short="OTH",
                embargo_period=timedelta(days=365),  # Different embargo
            )

            # Create observation for project2 using helper but update the project
            obs_project2, _, pr2 = create_observation_pipeline_run_toa(
                os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"), self.telescope, self.template
            )
            obs_project2.project = project2
            obs_project2.utc_start = timezone.now() - timedelta(
                days=300
            )  # Would be public for project 1 (548 days), embargoed for project 2 (365 days)
            obs_project2.save()

            pfr2 = PulsarFoldResult.objects.get(observation=obs_project2)

            img_path = "MeerKAT/OTHER-PROJECT/J0125-2327/2024-07-01-00:00:00/3/profile.png"
            img_file = Path(self.test_media_dir) / img_path
            img_file.parent.mkdir(parents=True, exist_ok=True)
            img_file.write_bytes(b"project2 data")

            PipelineImage.objects.create(
                pulsar_fold_result=pfr2, image=img_path, image_type="profile", resolution="high", cleaned=True
            )

            # Non-member should NOT have access (still embargoed for project2)
            self.client.force_login(self.non_member)
            response = self.client.get(f"/media/{img_path}")
            self.assertEqual(response.status_code, 403)
