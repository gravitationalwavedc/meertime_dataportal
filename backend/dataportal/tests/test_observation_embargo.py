from datetime import datetime, timedelta
import os

import pytz
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from dataportal.models import (
    Observation,
    Project,
    ProjectMembership,
)
from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import (
    create_basic_data,
    create_observation_pipeline_run_toa,
)

User = get_user_model()
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


class ObservationEmbargoTestCase(BaseTestCaseWithTempMedia):
    """Test observation embargo and restriction logic with project membership"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all test methods in this class"""
        # Use testing utilities to create base data
        telescope, cls.project1, ephemeris, template = create_basic_data()
        cls.pulsar = ephemeris.pulsar

        # Create a second project for cross-project testing
        cls.project2 = Project.objects.create(
            main_project=cls.project1.main_project,
            code="RELBIN",
            short="RELBIN",
            description="Relativistic Binaries",
            embargo_period=timedelta(days=365),  # 12 months
        )

        # Create users
        cls.superuser = User.objects.create_user(
            username="superuser",
            email="superuser@test.com",
            password="testpass123",
            is_superuser=True,
            is_staff=True,
        )
        cls.project1_member = User.objects.create_user(
            username="project1_member",
            email="project1@test.com",
            password="testpass123",
        )
        cls.project2_member = User.objects.create_user(
            username="project2_member",
            email="project2@test.com",
            password="testpass123",
        )
        cls.non_member = User.objects.create_user(
            username="nonmember",
            email="nonmember@test.com",
            password="testpass123",
        )

        # Create project memberships
        ProjectMembership.objects.create(
            user=cls.project1_member,
            project=cls.project1,
            role=ProjectMembership.RoleChoices.MEMBER,
        )
        ProjectMembership.objects.create(
            user=cls.project2_member,
            project=cls.project2,
            role=ProjectMembership.RoleChoices.MEMBER,
        )

        # Create test observations with different embargo states
        # Use existing JSON test data to create properly-formed observations
        json_file = os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json")

        # Create embargoed observation in project1 (use template's project, will reassign)
        obs_embargoed_p1, _, _ = create_observation_pipeline_run_toa(json_file, telescope, template, make_toas=False)
        cls.embargoed_obs_project1 = obs_embargoed_p1
        # Reassign to project1 with recent date
        now = datetime.now(tz=pytz.UTC)
        cls.embargoed_obs_project1.project = cls.project1
        cls.embargoed_obs_project1.utc_start = now - timedelta(days=30)
        cls.embargoed_obs_project1.save()

        # Create public (non-embargoed) observation in project1
        obs_public_p1, _, _ = create_observation_pipeline_run_toa(json_file, telescope, template, make_toas=False)
        cls.public_obs_project1 = obs_public_p1
        cls.public_obs_project1.project = cls.project1
        cls.public_obs_project1.utc_start = now - timedelta(days=600)  # 20 months ago
        cls.public_obs_project1.save()

        # Create embargoed observation in project2
        obs_embargoed_p2, _, _ = create_observation_pipeline_run_toa(json_file, telescope, template, make_toas=False)
        cls.embargoed_obs_project2 = obs_embargoed_p2
        cls.embargoed_obs_project2.project = cls.project2
        cls.embargoed_obs_project2.utc_start = now - timedelta(days=30)
        cls.embargoed_obs_project2.save()

    # ===== is_embargoed() Tests =====

    def test_embargoed_observation(self):
        """Recent observations should be embargoed"""
        self.assertTrue(self.embargoed_obs_project1.is_embargoed)
        self.assertTrue(self.embargoed_obs_project2.is_embargoed)

    def test_public_observation(self):
        """Old observations past embargo period should not be embargoed"""
        self.assertFalse(self.public_obs_project1.is_embargoed)

    # ===== is_restricted() Tests - Superuser =====

    def test_superuser_can_access_embargoed_data(self):
        """Superusers can access all embargoed observations"""
        self.assertFalse(self.embargoed_obs_project1.is_restricted(self.superuser))
        self.assertFalse(self.embargoed_obs_project2.is_restricted(self.superuser))

    def test_superuser_can_access_public_data(self):
        """Superusers can access public observations"""
        self.assertFalse(self.public_obs_project1.is_restricted(self.superuser))

    # ===== is_restricted() Tests - Project Members =====

    def test_project_member_can_access_own_embargoed_data(self):
        """Project members can access embargoed observations from their project"""
        self.assertFalse(self.embargoed_obs_project1.is_restricted(self.project1_member))
        self.assertFalse(self.embargoed_obs_project2.is_restricted(self.project2_member))

    def test_project_member_cannot_access_other_embargoed_data(self):
        """Project members cannot access embargoed observations from other projects"""
        self.assertTrue(self.embargoed_obs_project2.is_restricted(self.project1_member))
        self.assertTrue(self.embargoed_obs_project1.is_restricted(self.project2_member))

    def test_project_member_can_access_public_data(self):
        """Project members can access public observations from any project"""
        self.assertFalse(self.public_obs_project1.is_restricted(self.project1_member))
        self.assertFalse(self.public_obs_project1.is_restricted(self.project2_member))

    # ===== is_restricted() Tests - Non-Members =====

    def test_non_member_cannot_access_embargoed_data(self):
        """Non-members cannot access any embargoed observations"""
        self.assertTrue(self.embargoed_obs_project1.is_restricted(self.non_member))
        self.assertTrue(self.embargoed_obs_project2.is_restricted(self.non_member))

    def test_non_member_can_access_public_data(self):
        """Non-members can access public observations"""
        self.assertFalse(self.public_obs_project1.is_restricted(self.non_member))

    # ===== is_restricted() Tests - Anonymous Users =====

    def test_anonymous_user_cannot_access_embargoed_data(self):
        """Anonymous users cannot access embargoed observations"""
        anonymous = AnonymousUser()
        self.assertTrue(self.embargoed_obs_project1.is_restricted(anonymous))
        self.assertTrue(self.embargoed_obs_project2.is_restricted(anonymous))

    def test_anonymous_user_can_access_public_data(self):
        """Anonymous users can access public observations"""
        anonymous = AnonymousUser()
        self.assertFalse(self.public_obs_project1.is_restricted(anonymous))

    # ===== is_restricted() Tests - Inactive Memberships =====

    def test_inactive_membership_cannot_access_embargoed_data(self):
        """Users with inactive memberships cannot access embargoed observations"""
        # Deactivate the membership
        membership = ProjectMembership.objects.get(
            user=self.project1_member,
            project=self.project1,
        )
        membership.is_active = False
        membership.save()

        # Should now be restricted
        self.assertTrue(self.embargoed_obs_project1.is_restricted(self.project1_member))

        # But can still access public data
        self.assertFalse(self.public_obs_project1.is_restricted(self.project1_member))
