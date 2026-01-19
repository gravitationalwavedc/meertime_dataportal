"""
Test Template model access control methods.
Tests is_embargoed property and is_restricted(user) method.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from dataportal.models import Project, ProjectMembership, Pulsar, Template
from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import create_basic_data

User = get_user_model()


class TemplateModelTestCase(BaseTestCaseWithTempMedia):
    """Test Template model access control logic"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all test methods in this class"""
        # Use existing test helper to create basic fixtures
        telescope, project, ephemeris, template = create_basic_data()
        cls.telescope = telescope
        cls.pulsar = Pulsar.objects.get(name="J0125-2327")
        cls.project = Project.objects.get(code="SCI-20180516-MB-05")

        # Create test users
        cls.superuser = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123", role="ADMIN"
        )
        cls.project_member = User.objects.create_user(
            username="member", email="member@test.com", password="member123", role="UNRESTRICTED"
        )
        cls.non_member = User.objects.create_user(
            username="nonmember", email="nonmember@test.com", password="nonmember123", role="UNRESTRICTED"
        )

        # Create active membership
        ProjectMembership.objects.create(
            user=cls.project_member, project=cls.project, role=ProjectMembership.RoleChoices.MEMBER
        )

    # ===== is_embargoed Property Tests =====

    def test_template_is_embargoed_when_recent(self):
        """Template is embargoed when created within embargo period"""
        now = timezone.now()

        # Create template 30 days ago (within default 548 day embargo)
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=30)
        template.save()

        self.assertTrue(template.is_embargoed)

    def test_template_is_not_embargoed_when_old(self):
        """Template is not embargoed when created before embargo period"""
        now = timezone.now()

        # Create template 600 days ago (beyond default 548 day embargo)
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=600)
        template.save()

        self.assertFalse(template.is_embargoed)

    def test_template_embargo_boundary(self):
        """Template embargo status at boundary (exactly embargo period)"""
        now = timezone.now()

        # Create template exactly at embargo period boundary
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        # Set to exactly embargo period ago + 1 second (should not be embargoed)
        template.created_at = now - self.project.embargo_period - timedelta(seconds=1)
        template.save()

        # Just past the boundary, should not be embargoed
        self.assertFalse(template.is_embargoed)

    # ===== is_restricted() Method Tests - Authentication =====

    def test_anonymous_user_restricted_from_all_templates(self):
        """Anonymous users cannot access any templates (always restricted)"""
        now = timezone.now()

        # Create public template
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=600)
        template.save()

        # Anonymous user (None or unauthenticated)
        anonymous = AnonymousUser()
        self.assertTrue(template.is_restricted(anonymous))

    # ===== is_restricted() Method Tests - Superuser =====

    def test_superuser_not_restricted_from_embargoed_template(self):
        """Superusers can access all templates including embargoed"""
        now = timezone.now()

        # Create embargoed template
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=30)
        template.save()

        self.assertTrue(template.is_embargoed)
        self.assertFalse(template.is_restricted(self.superuser))

    # ===== is_restricted() Method Tests - Public Templates =====

    def test_authenticated_user_not_restricted_from_public_template(self):
        """Authenticated users can access non-embargoed templates"""
        now = timezone.now()

        # Create public template (beyond default 548 day embargo)
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=600)
        template.save()

        self.assertFalse(template.is_embargoed)
        self.assertFalse(template.is_restricted(self.non_member))

    # ===== is_restricted() Method Tests - Embargoed Templates =====

    def test_non_member_restricted_from_embargoed_template(self):
        """Non-members cannot access embargoed templates"""
        now = timezone.now()

        # Create embargoed template
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=30)
        template.save()

        self.assertTrue(template.is_embargoed)
        self.assertTrue(template.is_restricted(self.non_member))

    def test_project_member_not_restricted_from_embargoed_template(self):
        """Project members can access embargoed templates from their project"""
        now = timezone.now()

        # Create embargoed template
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=30)
        template.save()

        self.assertTrue(template.is_embargoed)
        self.assertFalse(template.is_restricted(self.project_member))

    def test_inactive_member_restricted_from_embargoed_template(self):
        """Users with inactive memberships cannot access embargoed templates"""
        now = timezone.now()

        # Create embargoed template
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=30)
        template.save()

        # Deactivate membership
        membership = ProjectMembership.objects.get(user=self.project_member, project=self.project)
        membership.is_active = False
        membership.save()

        self.assertTrue(template.is_embargoed)
        self.assertTrue(template.is_restricted(self.project_member))

    # ===== is_restricted() Method Tests - Edge Cases =====

    def test_member_of_different_project_restricted(self):
        """Member of different project cannot access embargoed template"""
        now = timezone.now()

        # Create second project (without telescope parameter)
        # Get main_project from existing project
        other_project = Project.objects.create(code="OTHER", short="OTH", main_project=self.project.main_project)
        other_member = User.objects.create_user(
            username="othermember", email="other@test.com", password="other123", role="UNRESTRICTED"
        )
        ProjectMembership.objects.create(
            user=other_member, project=other_project, role=ProjectMembership.RoleChoices.MEMBER
        )

        # Create embargoed template in original project
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=self.project,
            band="LBAND",
            template_file="test.std",
        )
        template.created_at = now - timedelta(days=30)
        template.save()

        # Member of other project should be restricted
        self.assertTrue(template.is_embargoed)
        self.assertTrue(template.is_restricted(other_member))
