from django.contrib.auth import get_user_model
from django.test import TestCase

from dataportal.models import (
    MainProject,
    Project,
    ProjectMembership,
    ProjectMembershipRequest,
    Telescope,
)

User = get_user_model()


class ProjectMembershipTest(TestCase):
    def setUp(self):
        """Set up test users and projects"""
        # Create users
        self.owner_user = User.objects.create_user(
            username="owner@test.com",
            email="owner@test.com",
            password="testpass123",
        )
        self.manager_user = User.objects.create_user(
            username="manager@test.com",
            email="manager@test.com",
            password="testpass123",
        )
        self.member_user = User.objects.create_user(
            username="member@test.com",
            email="member@test.com",
            password="testpass123",
        )
        self.non_member_user = User.objects.create_user(
            username="nonmember@test.com",
            email="nonmember@test.com",
            password="testpass123",
        )

        # Create telescope and main project
        self.telescope = Telescope.objects.create(name="Test Telescope")
        self.main_project = MainProject.objects.create(
            name="Test Main Project",
            telescope=self.telescope,
        )

        # Create project
        self.project = Project.objects.create(
            code="TEST-PROJECT-01",
            short="TEST",
            main_project=self.main_project,
        )

        # Create memberships
        ProjectMembership.objects.create(
            user=self.owner_user,
            project=self.project,
            role=ProjectMembership.RoleChoices.OWNER,
        )
        ProjectMembership.objects.create(
            user=self.manager_user,
            project=self.project,
            role=ProjectMembership.RoleChoices.MANAGER,
        )
        ProjectMembership.objects.create(
            user=self.member_user,
            project=self.project,
            role=ProjectMembership.RoleChoices.MEMBER,
        )

    def test_project_membership_creation(self):
        """Test that project memberships are created correctly"""
        self.assertEqual(ProjectMembership.objects.count(), 3)

        owner_membership = ProjectMembership.objects.get(user=self.owner_user)
        self.assertEqual(owner_membership.role, ProjectMembership.RoleChoices.OWNER)
        self.assertEqual(owner_membership.project, self.project)

    def test_project_membership_unique_together(self):
        """Test that a user cannot have duplicate memberships for the same project"""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            ProjectMembership.objects.create(
                user=self.owner_user,
                project=self.project,
                role=ProjectMembership.RoleChoices.MEMBER,
            )

    def test_project_is_owner_method(self):
        """Test the Project.is_owner method"""
        self.assertTrue(self.project.is_owner(self.owner_user))
        self.assertFalse(self.project.is_owner(self.manager_user))
        self.assertFalse(self.project.is_owner(self.member_user))
        self.assertFalse(self.project.is_owner(self.non_member_user))

    def test_project_is_manager_method(self):
        """Test the Project.is_manager method"""
        # is_manager checks for both MANAGER and OWNER roles
        self.assertTrue(self.project.is_manager(self.owner_user))
        self.assertTrue(self.project.is_manager(self.manager_user))
        self.assertFalse(self.project.is_manager(self.member_user))
        self.assertFalse(self.project.is_manager(self.non_member_user))


class ProjectMembershipRequestTest(TestCase):
    def setUp(self):
        """Set up test users, projects, and membership requests"""
        # Create users
        self.owner_user = User.objects.create_user(
            username="owner@test.com",
            email="owner@test.com",
            password="testpass123",
        )
        self.manager_user = User.objects.create_user(
            username="manager@test.com",
            email="manager@test.com",
            password="testpass123",
        )
        self.requesting_user = User.objects.create_user(
            username="requester@test.com",
            email="requester@test.com",
            password="testpass123",
        )
        self.another_requesting_user = User.objects.create_user(
            username="requester2@test.com",
            email="requester2@test.com",
            password="testpass123",
        )

        # Create telescope and main project
        self.telescope = Telescope.objects.create(name="Test Telescope")
        self.main_project = MainProject.objects.create(
            name="Test Main Project",
            telescope=self.telescope,
        )

        # Create projects
        self.project1 = Project.objects.create(
            code="TEST-PROJECT-01",
            short="TEST1",
            main_project=self.main_project,
        )
        self.project2 = Project.objects.create(
            code="TEST-PROJECT-02",
            short="TEST2",
            main_project=self.main_project,
        )

        # Create memberships for project1
        ProjectMembership.objects.create(
            user=self.owner_user,
            project=self.project1,
            role=ProjectMembership.RoleChoices.OWNER,
        )
        ProjectMembership.objects.create(
            user=self.manager_user,
            project=self.project1,
            role=ProjectMembership.RoleChoices.MANAGER,
        )

        # Create pending membership requests
        self.request1 = ProjectMembershipRequest.objects.create(
            user=self.requesting_user,
            project=self.project1,
            message="Please let me join project 1",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        self.request2 = ProjectMembershipRequest.objects.create(
            user=self.another_requesting_user,
            project=self.project1,
            message="I also want to join project 1",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )

    def test_membership_request_creation(self):
        """Test that membership requests are created correctly"""
        self.assertEqual(ProjectMembershipRequest.objects.count(), 2)
        self.assertEqual(self.request1.status, ProjectMembershipRequest.StatusChoices.PENDING)
        self.assertEqual(self.request1.user, self.requesting_user)
        self.assertEqual(self.request1.project, self.project1)

    def test_membership_request_create_classmethod(self):
        """Test the ProjectMembershipRequest.create classmethod"""
        new_user = User.objects.create_user(
            username="newuser@test.com",
            email="newuser@test.com",
            password="testpass123",
        )
        request = ProjectMembershipRequest.create(
            user=new_user,
            project=self.project2,
            message="Test message",
        )
        self.assertIsNotNone(request)
        self.assertEqual(request.user, new_user)
        self.assertEqual(request.project, self.project2)
        self.assertEqual(request.message, "Test message")
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.PENDING)

    def test_user_requests_classmethod(self):
        """Test the ProjectMembershipRequest.user_requests classmethod"""
        # Get requests for the requesting user
        user_requests = ProjectMembershipRequest.user_requests(self.requesting_user)
        self.assertEqual(user_requests.count(), 1)
        self.assertEqual(user_requests.first(), self.request1)

        # Create another request for the same user in a different project
        ProjectMembershipRequest.objects.create(
            user=self.requesting_user,
            project=self.project2,
            message="Another request",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        user_requests = ProjectMembershipRequest.user_requests(self.requesting_user)
        self.assertEqual(user_requests.count(), 2)

        # Verify ordering (most recent first)
        self.assertEqual(user_requests.first().project, self.project2)

    def test_membership_approval_requests_classmethod_as_owner(self):
        """Test the ProjectMembershipRequest.membership_approval_requests classmethod for project owner"""
        # Get requests for project1 as owner
        project_requests = ProjectMembershipRequest.membership_approval_requests(
            self.owner_user,
        )
        self.assertEqual(project_requests.count(), 2)
        self.assertIn(self.request1, project_requests)
        self.assertIn(self.request2, project_requests)

    def test_membership_approval_requests_classmethod_as_manager(self):
        """Test the ProjectMembershipRequest.membership_approval_requests classmethod for project manager"""
        # Get requests for project1 as manager
        project_requests = ProjectMembershipRequest.membership_approval_requests(
            self.manager_user,
        )
        self.assertEqual(project_requests.count(), 2)
        self.assertIn(self.request1, project_requests)
        self.assertIn(self.request2, project_requests)

    def test_membership_approval_requests_classmethod_as_non_manager(self):
        """Test the ProjectMembershipRequest.membership_approval_requests classmethod for non-manager"""
        from graphql import GraphQLError

        # Non-managers should get a permission error
        with self.assertRaises(GraphQLError) as context:
            ProjectMembershipRequest.membership_approval_requests(
                self.requesting_user,
            )
        self.assertIn("You do not have permission to view approval requests", str(context.exception))

    def test_membership_approval_requests_ordering(self):
        """Test that membership_approval_requests returns results ordered by requested_at"""
        # Get requests as owner
        project_requests = ProjectMembershipRequest.membership_approval_requests(
            self.owner_user,
        )
        # Should be ordered by requested_at (oldest first)
        self.assertEqual(project_requests.first(), self.request1)

    def test_multiple_requests_allowed_with_different_status(self):
        """Test that a user can have multiple requests for the same project with different statuses"""
        # This is now allowed since we removed the unique_together constraint
        # Create an approved request
        approved_request = ProjectMembershipRequest.objects.create(
            user=self.requesting_user,
            project=self.project1,
            message="Duplicate request - approved",
            status=ProjectMembershipRequest.StatusChoices.APPROVED,
        )
        self.assertIsNotNone(approved_request)

        # Now there should be 2 requests for this user/project combination
        requests = ProjectMembershipRequest.objects.filter(user=self.requesting_user, project=self.project1)
        self.assertEqual(requests.count(), 2)

    def test_membership_request_status_choices(self):
        """Test that status can be updated through the lifecycle"""
        # Create a new request
        request = ProjectMembershipRequest.objects.create(
            user=self.another_requesting_user,
            project=self.project2,
            message="Test request",
        )
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.PENDING)

        # Update to approved
        request.status = ProjectMembershipRequest.StatusChoices.APPROVED
        request.save()
        request.refresh_from_db()
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.APPROVED)

        # Create another and reject it
        request2 = ProjectMembershipRequest.objects.create(
            user=self.requesting_user,
            project=self.project2,
            message="Another test request",
        )
        request2.status = ProjectMembershipRequest.StatusChoices.REJECTED
        request2.save()
        request2.refresh_from_db()
        self.assertEqual(request2.status, ProjectMembershipRequest.StatusChoices.REJECTED)

    def test_membership_approval_requests_only_returns_for_specific_project(self):
        """Test that membership_approval_requests only returns pending requests for projects user manages"""
        # Create request for project2
        ProjectMembershipRequest.objects.create(
            user=self.requesting_user,
            project=self.project2,
            message="Request for project 2",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )

        # Owner of project1 should only see project1 requests since they don't manage project2
        project1_requests = ProjectMembershipRequest.membership_approval_requests(
            self.owner_user,
        )
        self.assertEqual(project1_requests.count(), 2)
        for request in project1_requests:
            self.assertEqual(request.project, self.project1)

    def test_membership_approval_requests_with_approved_and_rejected_requests(self):
        """Test that membership_approval_requests only returns pending requests"""
        # Update request1 to approved
        self.request1.status = ProjectMembershipRequest.StatusChoices.APPROVED
        self.request1.save()

        # Create a new user for the rejected request
        new_user = User.objects.create_user(
            username="newuser@test.com",
            email="newuser@test.com",
            password="testpass123",
        )

        # Create a rejected request with the new user
        ProjectMembershipRequest.objects.create(
            user=new_user,
            project=self.project1,
            message="Rejected request",
            status=ProjectMembershipRequest.StatusChoices.REJECTED,
        )

        # Get pending requests for project1
        project_requests = ProjectMembershipRequest.membership_approval_requests(
            self.owner_user,
        )
        # Should return only pending requests (request2)
        self.assertEqual(project_requests.count(), 1)
        self.assertEqual(project_requests.first(), self.request2)

    def test_request_to_join_success(self):
        """Test that request_to_join successfully creates a request for a new user"""
        new_user = User.objects.create_user(
            username="newuser@test.com",
            email="newuser@test.com",
            password="testpass123",
        )

        result = ProjectMembershipRequest.request_to_join(
            user=new_user,
            project=self.project1,
            message="I want to join this project",
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["request"])
        self.assertIsNone(result["error"])
        self.assertEqual(result["request"].user, new_user)
        self.assertEqual(result["request"].project, self.project1)
        self.assertEqual(result["request"].message, "I want to join this project")
        self.assertEqual(result["request"].status, ProjectMembershipRequest.StatusChoices.PENDING)

    def test_request_to_join_fails_if_already_active_member(self):
        """Test that request_to_join fails if user is already an active member"""
        result = ProjectMembershipRequest.request_to_join(
            user=self.owner_user,
            project=self.project1,
            message="I want to join",
        )

        self.assertFalse(result["success"])
        self.assertIsNone(result["request"])
        self.assertIn("already a member", result["error"])

    def test_request_to_join_fails_if_pending_request_exists(self):
        """Test that request_to_join fails if user already has a pending request"""
        result = ProjectMembershipRequest.request_to_join(
            user=self.requesting_user,
            project=self.project1,
            message="Another request",
        )

        self.assertFalse(result["success"])
        self.assertIsNone(result["request"])
        self.assertIn("already have a pending request", result["error"])

    def test_request_to_join_allows_rejoin_after_leaving(self):
        """Test that a user can request to join again after leaving a project"""
        # Create a user who was a member but left
        former_member = User.objects.create_user(
            username="former@test.com",
            email="former@test.com",
            password="testpass123",
        )

        # Create an inactive membership (they left)
        ProjectMembership.objects.create(
            user=former_member,
            project=self.project1,
            role=ProjectMembership.RoleChoices.MEMBER,
            is_active=False,
        )

        # They should be able to request to join again
        result = ProjectMembershipRequest.request_to_join(
            user=former_member,
            project=self.project1,
            message="I want to rejoin",
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["request"])
        self.assertIsNone(result["error"])

    def test_request_to_join_allows_request_after_rejection(self):
        """Test that a user can request again after being rejected"""
        new_user = User.objects.create_user(
            username="rejected@test.com",
            email="rejected@test.com",
            password="testpass123",
        )

        # Create a rejected request
        ProjectMembershipRequest.objects.create(
            user=new_user,
            project=self.project1,
            message="First request",
            status=ProjectMembershipRequest.StatusChoices.REJECTED,
        )

        # They should be able to request again
        result = ProjectMembershipRequest.request_to_join(
            user=new_user,
            project=self.project1,
            message="Second request",
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["request"])
        self.assertIsNone(result["error"])

        # Verify there are now 2 requests for this user/project
        requests = ProjectMembershipRequest.objects.filter(user=new_user, project=self.project1)
        self.assertEqual(requests.count(), 2)

    def test_request_to_join_allows_request_after_approval_and_leaving(self):
        """Test the full lifecycle: request -> approve -> leave -> request again"""
        new_user = User.objects.create_user(
            username="lifecycle@test.com",
            email="lifecycle@test.com",
            password="testpass123",
        )

        # Step 1: Create and approve a request
        first_request = ProjectMembershipRequest.objects.create(
            user=new_user,
            project=self.project1,
            message="First request",
        )
        first_request.approve(approver=self.owner_user)

        # Step 2: User leaves the project
        membership = ProjectMembership.objects.get(user=new_user, project=self.project1)
        membership.is_active = False
        membership.save()

        # Step 3: User requests to join again
        result = ProjectMembershipRequest.request_to_join(
            user=new_user,
            project=self.project1,
            message="I want to rejoin",
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["request"])
        self.assertIsNone(result["error"])

        # Verify there are now 2 requests for this user/project (original approved + new pending)
        requests = ProjectMembershipRequest.objects.filter(user=new_user, project=self.project1)
        self.assertEqual(requests.count(), 2)
        self.assertEqual(requests.filter(status=ProjectMembershipRequest.StatusChoices.APPROVED).count(), 1)
        self.assertEqual(requests.filter(status=ProjectMembershipRequest.StatusChoices.PENDING).count(), 1)

    def test_request_to_join_with_no_message(self):
        """Test that request_to_join works without a message"""
        new_user = User.objects.create_user(
            username="nomessage@test.com",
            email="nomessage@test.com",
            password="testpass123",
        )

        result = ProjectMembershipRequest.request_to_join(
            user=new_user,
            project=self.project1,
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["request"])
        self.assertEqual(result["request"].message, "")

    def test_approve_reactivates_inactive_membership(self):
        """Test that approving a request for a former member reactivates their membership"""
        # Create a user who was a member but left
        former_member = User.objects.create_user(
            username="former@test.com",
            email="former@test.com",
            password="testpass123",
        )

        # Create an inactive membership (they left)
        old_membership = ProjectMembership.objects.create(
            user=former_member,
            project=self.project1,
            role=ProjectMembership.RoleChoices.MEMBER,
            is_active=False,
            approved_by=self.owner_user,
        )
        old_membership_id = old_membership.id

        # They request to rejoin
        request = ProjectMembershipRequest.objects.create(
            user=former_member,
            project=self.project1,
            message="I want to rejoin",
        )

        # Approve the request
        request.approve(approver=self.manager_user)

        # Check that the old membership was reactivated, not a new one created
        membership = ProjectMembership.objects.get(user=former_member, project=self.project1)
        self.assertEqual(membership.id, old_membership_id)  # Same membership object
        self.assertTrue(membership.is_active)  # Now active
        self.assertEqual(membership.approved_by, self.manager_user)  # Updated approver

        # Verify only one membership exists
        membership_count = ProjectMembership.objects.filter(user=former_member, project=self.project1).count()
        self.assertEqual(membership_count, 1)
