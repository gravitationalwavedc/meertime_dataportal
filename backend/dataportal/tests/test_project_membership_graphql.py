from django.contrib.auth import get_user_model
from django.core import mail
from graphene_django.utils.testing import GraphQLTestCase
from graphql_relay import to_global_id

from dataportal.models import (
    MainProject,
    Project,
    ProjectMembership,
    ProjectMembershipRequest,
    Telescope,
)

User = get_user_model()


class ProjectMembershipGraphQLTestCase(GraphQLTestCase):
    """Test GraphQL authorization for project membership operations"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all test methods in this class."""
        # Create telescope and main project
        cls.telescope = Telescope.objects.create(name="MeerKAT")
        cls.main_project = MainProject.objects.create(
            name="MeerTime",
            telescope=cls.telescope,
        )

        # Create projects
        cls.project1 = Project.objects.create(
            main_project=cls.main_project,
            code="TPA",
            short="TPA",
            description="Thousand Pulsar Array",
        )
        cls.project2 = Project.objects.create(
            main_project=cls.main_project,
            code="RELBIN",
            short="RELBIN",
            description="Relativistic Binaries",
        )

        # Create users
        cls.superuser = User.objects.create_user(
            username="superuser",
            email="superuser@test.com",
            password="testpass123",
            is_superuser=True,
            is_staff=True,
        )
        cls.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="testpass123",
        )
        cls.manager = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="testpass123",
        )
        cls.member = User.objects.create_user(
            username="member",
            email="member@test.com",
            password="testpass123",
        )
        cls.non_member = User.objects.create_user(
            username="nonmember",
            email="nonmember@test.com",
            password="testpass123",
        )
        cls.another_user = User.objects.create_user(
            username="another",
            email="another@test.com",
            password="testpass123",
        )

        # Create memberships for project1
        ProjectMembership.objects.create(
            user=cls.owner,
            project=cls.project1,
            role=ProjectMembership.RoleChoices.OWNER,
        )
        ProjectMembership.objects.create(
            user=cls.manager,
            project=cls.project1,
            role=ProjectMembership.RoleChoices.MANAGER,
        )
        ProjectMembership.objects.create(
            user=cls.member,
            project=cls.project1,
            role=ProjectMembership.RoleChoices.MEMBER,
        )

    # ===== CreateProjectMembershipRequest Tests =====

    def test_create_request_requires_login(self):
        """Unauthenticated users cannot create membership requests"""
        mutation = """
            mutation {
                createProjectMembershipRequest(input: {projectCode: "TPA", message: "Please let me join"}) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        self.assertResponseHasErrors(response)
        self.assertIn("must be logged in", str(response.content))

    def test_create_request_authenticated(self):
        """Authenticated users can create membership requests"""
        self._client.force_login(self.non_member)
        initial_count = ProjectMembershipRequest.objects.count()

        mutation = """
            mutation {
                createProjectMembershipRequest(input: {projectCode: "TPA", message: "Please let me join"}) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertTrue(content["data"]["createProjectMembershipRequest"]["ok"])

        # Verify database state
        self.assertEqual(ProjectMembershipRequest.objects.count(), initial_count + 1)
        request = ProjectMembershipRequest.objects.latest("requested_at")
        self.assertEqual(request.user, self.non_member)
        self.assertEqual(request.project, self.project1)
        self.assertEqual(request.message, "Please let me join")
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.PENDING)

    def test_create_request_sends_email_to_managers(self):
        """Creating a request sends email to all project managers/owners"""
        self._client.force_login(self.non_member)

        mutation = """
            mutation {
                createProjectMembershipRequest(input: {projectCode: "TPA", message: "Please let me join"}) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertTrue(content["data"]["createProjectMembershipRequest"]["ok"])

        # Verify emails were sent to both owner and manager
        self.assertEqual(len(mail.outbox), 2)

        # Check recipients
        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn(self.owner.email, recipients)
        self.assertIn(self.manager.email, recipients)

        # Check email content
        for email in mail.outbox:
            self.assertIn("New membership request", email.subject)
            self.assertIn("TPA", email.subject)
            self.assertIn("Please let me join", email.body)

    # ===== RemoveProjectMembershipRequest Tests =====

    def test_remove_request_requires_login(self):
        """Unauthenticated users cannot remove membership requests"""
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                removeProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    deletedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        self.assertResponseHasErrors(response)
        self.assertIn("must be logged in", str(response.content))

    def test_remove_own_request(self):
        """Users can remove their own membership requests"""
        self._client.force_login(self.non_member)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)
        db_request_id = request.id

        mutation = f"""
            mutation {{
                removeProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    deletedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["removeProjectMembershipRequest"]["deletedProjectMembershipRequestId"],
            request_id,
        )
        self.assertEqual(len(content["data"]["removeProjectMembershipRequest"]["errors"]), 0)

        # Verify database state - request should be deleted
        self.assertFalse(ProjectMembershipRequest.objects.filter(id=db_request_id).exists())

    def test_cannot_remove_others_request(self):
        """Users cannot remove other users' membership requests"""
        self._client.force_login(self.another_user)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)
        db_request_id = request.id

        mutation = f"""
            mutation {{
                removeProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    deletedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertIsNone(content["data"]["removeProjectMembershipRequest"]["deletedProjectMembershipRequestId"])
        self.assertIn(
            "You do not have permission to remove this request.",
            content["data"]["removeProjectMembershipRequest"]["errors"],
        )

        # Verify database state - request should still exist
        self.assertTrue(ProjectMembershipRequest.objects.filter(id=db_request_id).exists())

    # ===== ApproveProjectMembershipRequest Tests =====

    def test_approve_request_requires_login(self):
        """Unauthenticated users cannot approve membership requests"""
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                approveProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    approvedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        self.assertResponseHasErrors(response)
        self.assertIn("must be logged in", str(response.content))

    def test_member_cannot_approve_request(self):
        """Regular members cannot approve membership requests"""
        self._client.force_login(self.member)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                approveProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    approvedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertIsNone(content["data"]["approveProjectMembershipRequest"]["approvedProjectMembershipRequestId"])
        self.assertIn(
            "You do not have permission to approve this request.",
            content["data"]["approveProjectMembershipRequest"]["errors"],
        )

        # Verify database state - request should still be pending
        request.refresh_from_db()
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.PENDING)

        # Verify membership was NOT created
        self.assertFalse(
            ProjectMembership.objects.filter(
                user=self.non_member,
                project=self.project1,
            ).exists()
        )

    def test_manager_can_approve_request(self):
        """Managers can approve membership requests"""
        self._client.force_login(self.manager)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                approveProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    approvedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["approveProjectMembershipRequest"]["approvedProjectMembershipRequestId"],
            request_id,
        )
        self.assertEqual(len(content["data"]["approveProjectMembershipRequest"]["errors"]), 0)

        # Verify database state
        request.refresh_from_db()
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.APPROVED)

        # Verify membership was created
        membership = ProjectMembership.objects.filter(
            user=self.non_member,
            project=self.project1,
        ).first()
        self.assertIsNotNone(membership)
        self.assertTrue(membership.is_active)
        self.assertEqual(membership.approved_by, self.manager)

    def test_approve_request_sends_email_to_requester(self):
        """Approving a request sends email to the requester"""
        self._client.force_login(self.manager)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                approveProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    approvedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["approveProjectMembershipRequest"]["approvedProjectMembershipRequestId"],
            request_id,
        )

        # Verify email was sent to requester
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to[0], self.non_member.email)
        self.assertIn("was approved", email.subject)
        self.assertIn("TPA", email.subject)
        self.assertIn("manager", email.body)

    def test_owner_can_approve_request(self):
        """Owners can approve membership requests"""
        self._client.force_login(self.owner)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                approveProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    approvedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["approveProjectMembershipRequest"]["approvedProjectMembershipRequestId"],
            request_id,
        )

    def test_superuser_can_approve_request(self):
        """Superusers can approve any membership request"""
        self._client.force_login(self.superuser)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                approveProjectMembershipRequest(input: {{requestId: "{request_id}"}}) {{
                    approvedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["approveProjectMembershipRequest"]["approvedProjectMembershipRequestId"],
            request_id,
        )

    # ===== RejectProjectMembershipRequest Tests =====

    def test_reject_request_requires_login(self):
        """Unauthenticated users cannot reject membership requests"""
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                rejectProjectMembershipRequest(input: {{projectMembershipRequestId: "{request_id}"}}) {{
                    rejectedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        self.assertResponseHasErrors(response)
        self.assertIn("must be logged in", str(response.content))

    def test_member_cannot_reject_request(self):
        """Regular members cannot reject membership requests"""
        self._client.force_login(self.member)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                rejectProjectMembershipRequest(input: {{projectMembershipRequestId: "{request_id}"}}) {{
                    rejectedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertIsNone(content["data"]["rejectProjectMembershipRequest"]["rejectedProjectMembershipRequestId"])
        self.assertIn(
            "You do not have permission to reject this request.",
            content["data"]["rejectProjectMembershipRequest"]["errors"],
        )

        # Verify database state - request should still be pending
        request.refresh_from_db()
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.PENDING)

    def test_manager_can_reject_request(self):
        """Managers can reject membership requests"""
        self._client.force_login(self.manager)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                rejectProjectMembershipRequest(input: {{projectMembershipRequestId: "{request_id}"}}) {{
                    rejectedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["rejectProjectMembershipRequest"]["rejectedProjectMembershipRequestId"],
            request_id,
        )
        self.assertEqual(len(content["data"]["rejectProjectMembershipRequest"]["errors"]), 0)

        # Verify database state
        request.refresh_from_db()
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.REJECTED)

        # Verify membership was NOT created
        self.assertFalse(
            ProjectMembership.objects.filter(
                user=self.non_member,
                project=self.project1,
            ).exists()
        )

    def test_owner_can_reject_request(self):
        """Owners can reject membership requests"""
        self._client.force_login(self.owner)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                rejectProjectMembershipRequest(input: {{projectMembershipRequestId: "{request_id}"}}) {{
                    rejectedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["rejectProjectMembershipRequest"]["rejectedProjectMembershipRequestId"],
            request_id,
        )

    def test_superuser_can_reject_request(self):
        """Superusers can reject any membership request"""
        self._client.force_login(self.superuser)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)

        mutation = f"""
            mutation {{
                rejectProjectMembershipRequest(input: {{projectMembershipRequestId: "{request_id}"}}) {{
                    rejectedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["rejectProjectMembershipRequest"]["rejectedProjectMembershipRequestId"],
            request_id,
        )

    def test_reject_request_saves_note(self):
        """Rejection note is saved when provided"""
        self._client.force_login(self.manager)
        request = ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )
        request_id = to_global_id("ProjectMembershipRequestNode", request.id)
        rejection_note = "Unfortunately, we are not accepting new members at this time."

        mutation = f"""
            mutation {{
                rejectProjectMembershipRequest(input: {{
                    projectMembershipRequestId: "{request_id}",
                    note: "{rejection_note}"
                }}) {{
                    rejectedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content["data"]["rejectProjectMembershipRequest"]["rejectedProjectMembershipRequestId"],
            request_id,
        )

        # Verify rejection note was saved
        request.refresh_from_db()
        self.assertEqual(request.status, ProjectMembershipRequest.StatusChoices.REJECTED)
        self.assertEqual(request.rejection_note, rejection_note)

    def test_reject_request_handles_does_not_exist(self):
        """Test that rejecting a non-existent request returns appropriate error"""
        self._client.force_login(self.manager)
        # Use a valid global ID format but with a non-existent database ID
        fake_id = 99999
        request_id = to_global_id("ProjectMembershipRequestNode", fake_id)

        mutation = f"""
            mutation {{
                rejectProjectMembershipRequest(input: {{projectMembershipRequestId: "{request_id}"}}) {{
                    rejectedProjectMembershipRequestId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertIsNone(content["data"]["rejectProjectMembershipRequest"]["rejectedProjectMembershipRequestId"])
        self.assertIn(
            "The membership request does not exist.",
            content["data"]["rejectProjectMembershipRequest"]["errors"],
        )

    # ===== LeaveProject Tests =====

    def test_leave_project_requires_login(self):
        """Unauthenticated users cannot leave projects"""
        user_id = to_global_id("UserNode", self.member.id)
        project_id = to_global_id("ProjectNode", self.project1.id)

        mutation = f"""
            mutation {{
                leaveProject(input: {{userId: "{user_id}", projectId: "{project_id}"}}) {{
                    userId
                    projectId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        self.assertResponseHasErrors(response)
        self.assertIn("must be logged in", str(response.content))

    def test_member_can_leave_project(self):
        """Members can leave projects they belong to"""
        self._client.force_login(self.member)
        user_id = to_global_id("UserNode", self.member.id)
        project_id = to_global_id("ProjectNode", self.project1.id)

        mutation = f"""
            mutation {{
                leaveProject(input: {{userId: "{user_id}", projectId: "{project_id}"}}) {{
                    userId
                    projectId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["leaveProject"]["userId"], user_id)
        self.assertEqual(content["data"]["leaveProject"]["projectId"], project_id)

        # Verify database state - membership should be deactivated
        membership = ProjectMembership.objects.get(
            user=self.member,
            project=self.project1,
        )
        self.assertFalse(membership.is_active)

    def test_owner_cannot_leave_project(self):
        """Owners cannot leave their own projects"""
        self._client.force_login(self.owner)
        user_id = to_global_id("UserNode", self.owner.id)
        project_id = to_global_id("ProjectNode", self.project1.id)

        mutation = f"""
            mutation {{
                leaveProject(input: {{userId: "{user_id}", projectId: "{project_id}"}}) {{
                    userId
                    projectId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertIsNone(content["data"]["leaveProject"]["userId"])
        self.assertIn(
            "Project owners can't leave a project.",
            content["data"]["leaveProject"]["errors"],
        )

        # Verify database state - membership should still be active
        membership = ProjectMembership.objects.get(
            user=self.owner,
            project=self.project1,
        )
        self.assertTrue(membership.is_active)

    def test_manager_can_remove_member(self):
        """Managers can remove members from projects"""
        self._client.force_login(self.manager)
        user_id = to_global_id("UserNode", self.member.id)
        project_id = to_global_id("ProjectNode", self.project1.id)

        mutation = f"""
            mutation {{
                leaveProject(input: {{userId: "{user_id}", projectId: "{project_id}"}}) {{
                    userId
                    projectId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["leaveProject"]["userId"], user_id)

        # Verify database state - membership should be deactivated
        membership = ProjectMembership.objects.get(
            user=self.member,
            project=self.project1,
        )
        self.assertFalse(membership.is_active)

    def test_member_cannot_remove_others(self):
        """Regular members cannot remove other members"""
        self._client.force_login(self.member)
        user_id = to_global_id("UserNode", self.manager.id)
        project_id = to_global_id("ProjectNode", self.project1.id)

        mutation = f"""
            mutation {{
                leaveProject(input: {{userId: "{user_id}", projectId: "{project_id}"}}) {{
                    userId
                    projectId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertIsNone(content["data"]["leaveProject"]["userId"])
        self.assertIn(
            "You do not have permission.",
            content["data"]["leaveProject"]["errors"],
        )

        # Verify database state - membership should still be active
        membership = ProjectMembership.objects.get(
            user=self.manager,
            project=self.project1,
        )
        self.assertTrue(membership.is_active)

    def test_superuser_cannot_remove_owner(self):
        """Even superusers cannot remove project owners (owner check happens first)"""
        self._client.force_login(self.superuser)
        user_id = to_global_id("UserNode", self.owner.id)
        project_id = to_global_id("ProjectNode", self.project1.id)

        mutation = f"""
            mutation {{
                leaveProject(input: {{userId: "{user_id}", projectId: "{project_id}"}}) {{
                    userId
                    projectId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        # Owner check happens before permission check, so even superuser cannot remove owner
        self.assertIsNone(content["data"]["leaveProject"]["userId"])
        self.assertIn(
            "Project owners can't leave a project.",
            content["data"]["leaveProject"]["errors"],
        )

    def test_superuser_can_remove_non_owner_member(self):
        """Superusers can remove non-owner members"""
        self._client.force_login(self.superuser)
        user_id = to_global_id("UserNode", self.manager.id)
        project_id = to_global_id("ProjectNode", self.project1.id)

        mutation = f"""
            mutation {{
                leaveProject(input: {{userId: "{user_id}", projectId: "{project_id}"}}) {{
                    userId
                    projectId
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = response.json()
        self.assertResponseNoErrors(response)
        # Superuser has permission via can_edit, so removal succeeds
        self.assertEqual(content["data"]["leaveProject"]["userId"], user_id)

    # ===== Query Tests =====

    def test_pending_requests_query_requires_login(self):
        """Unauthenticated users cannot query pending membership requests"""
        query = """
            query {
                projectMembershipRequestsForApproval {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        response = self.query(query)
        self.assertResponseHasErrors(response)
        self.assertIn("must be logged in", str(response.content))

    def test_non_manager_cannot_query_pending_requests(self):
        """Non-managers cannot query pending membership requests"""
        self._client.force_login(self.member)
        query = """
            query {
                projectMembershipRequestsForApproval {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        response = self.query(query)
        self.assertResponseHasErrors(response)
        self.assertIn("You do not have permission to view approval requests", str(response.content))

    def test_manager_can_query_pending_requests(self):
        """Managers can query pending membership requests for their projects"""
        self._client.force_login(self.manager)
        # Create a pending request
        ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Please let me join",
        )

        query = """
            query {
                projectMembershipRequestsForApproval {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        response = self.query(query)
        content = response.json()
        self.assertResponseNoErrors(response)
        self.assertGreater(
            len(content["data"]["projectMembershipRequestsForApproval"]["edges"]),
            0,
        )

    def test_superuser_can_query_all_pending_requests(self):
        """Superusers can query all pending membership requests"""
        self._client.force_login(self.superuser)
        # Create pending requests for different projects
        ProjectMembershipRequest.objects.create(
            user=self.non_member,
            project=self.project1,
            message="Request 1",
        )
        ProjectMembershipRequest.objects.create(
            user=self.another_user,
            project=self.project2,
            message="Request 2",
        )

        query = """
            query {
                projectMembershipRequestsForApproval {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        response = self.query(query)
        content = response.json()
        self.assertResponseNoErrors(response)
        # Superuser sees all pending requests
        self.assertEqual(
            len(content["data"]["projectMembershipRequestsForApproval"]["edges"]),
            2,
        )
