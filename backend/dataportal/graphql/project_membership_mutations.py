import graphene
from django.contrib.auth import get_user_model
from dataportal.emails import send_membership_rejection_email
from dataportal.models import ProjectMembershipRequest, Project, ProjectMembership
from graphql_relay import from_global_id
from user_manage.graphql.decorators import login_required

User = get_user_model()


class CreateProjectMembershipRequestInput(graphene.InputObjectType):
    project_code = graphene.String(required=True)
    message = graphene.String(required=False)


class CreateProjectMembershipRequest(graphene.Mutation):
    class Arguments:
        input = CreateProjectMembershipRequestInput(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(root, info, input):
        try:
            project = Project.objects.get(code=input.project_code)
        except Project.DoesNotExist:
            return CreateProjectMembershipRequest(ok=False, errors=["The requested project no longer exists."])

        result = ProjectMembershipRequest.request_to_join(
            user=info.context.user,
            project=project,
            message=input.message,
        )

        if result["success"]:
            return CreateProjectMembershipRequest(ok=True, errors=[])
        else:
            return CreateProjectMembershipRequest(ok=False, errors=[result["error"]])


class RemoveProjectMembershipRequestInput(graphene.InputObjectType):
    request_id = graphene.ID(required=True)


class RemoveProjectMembershipRequest(graphene.Mutation):
    class Arguments:
        input = RemoveProjectMembershipRequestInput(required=True)

    deleted_project_membership_request_id = graphene.ID()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(root, info, input):
        model_type, request_id = from_global_id(input.request_id)

        if model_type != "ProjectMembershipRequestNode":
            return RemoveProjectMembershipRequest(
                deleted_project_membership_request_id=None,
                errors=["Invalid membership request ID."],
            )

        try:
            request = ProjectMembershipRequest.objects.get(id=request_id)

            # Check if user owns this request (only the requester can remove their own request)
            if request.user != info.context.user:
                return RemoveProjectMembershipRequest(
                    deleted_project_membership_request_id=None,
                    errors=["You do not have permission to remove this request."],
                )

            request.delete()
        except ProjectMembershipRequest.DoesNotExist:
            return RemoveProjectMembershipRequest(
                deleted_project_membership_request_id=None,
                errors=["The membership request does not exist."],
            )
        except Exception:
            return RemoveProjectMembershipRequest(
                deleted_project_membership_request_id=None,
                errors=["Something has gone wrong. Please try again later."],
            )

        return RemoveProjectMembershipRequest(
            deleted_project_membership_request_id=input.request_id,
            errors=[],
        )


class ApproveProjectMembershipRequestInput(graphene.InputObjectType):
    request_id = graphene.ID(required=True)


class ApproveProjectMembershipRequest(graphene.Mutation):

    class Arguments:
        input = ApproveProjectMembershipRequestInput(required=True)

    approved_project_membership_request_id = graphene.ID()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(root, info, input):
        model_type, request_id = from_global_id(input.request_id)

        if model_type != "ProjectMembershipRequestNode":
            return ApproveProjectMembershipRequest(
                approved_project_membership_request_id=None,
                errors=["Invalid membership request ID."],
            )

        try:
            request = ProjectMembershipRequest.objects.get(id=request_id)

            # Check if user is a manager of the project (superuser check is in is_manager)
            if not request.project.is_manager(info.context.user):
                return ApproveProjectMembershipRequest(
                    approved_project_membership_request_id=None,
                    errors=["You do not have permission to approve this request."],
                )

            request.approve(approver=info.context.user)
        except ProjectMembershipRequest.DoesNotExist:
            return ApproveProjectMembershipRequest(
                approved_project_membership_request_id=None,
                errors=["The membership request does not exist."],
            )
        except Exception as e:
            print(e)
            return ApproveProjectMembershipRequest(
                approved_project_membership_request_id=None,
                errors=["Something has gone wrong. Please try again later."],
            )

        return ApproveProjectMembershipRequest(
            approved_project_membership_request_id=input.request_id,
            errors=[],
        )


class RejectProjectMembershipRequestInput(graphene.InputObjectType):
    project_membership_request_id = graphene.ID(required=True)
    note = graphene.String(required=False)


class RejectProjectMembershipRequest(graphene.Mutation):

    class Arguments:
        input = RejectProjectMembershipRequestInput(required=True)

    rejected_project_membership_request_id = graphene.ID()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(root, info, input):

        model_type, membership_request_id = from_global_id(input.project_membership_request_id)

        if model_type != "ProjectMembershipRequestNode":
            return RejectProjectMembershipRequest(
                rejected_project_membership_request_id=None,
                errors=["Invalid membership request ID."],
            )

        try:
            membership_request = ProjectMembershipRequest.objects.get(id=membership_request_id)

            # Check if user is a manager of the project (superuser check is in is_manager)
            if not membership_request.project.is_manager(info.context.user):
                return RejectProjectMembershipRequest(
                    rejected_project_membership_request_id=None,
                    errors=["You do not have permission to reject this request."],
                )

            # Update status and save rejection note
            membership_request.status = ProjectMembershipRequest.StatusChoices.REJECTED
            membership_request.rejection_note = input.note or ""
            membership_request.save()

            # Send rejection email (non-blocking, log errors)
            send_membership_rejection_email(
                user=membership_request.user,
                project=membership_request.project,
                note=input.note,
            )

        except ProjectMembershipRequest.DoesNotExist:
            return RejectProjectMembershipRequest(
                rejected_project_membership_request_id=None,
                errors=["The membership request does not exist."],
            )
        except Exception as e:
            print(e)
            return RejectProjectMembershipRequest(
                rejected_project_membership_request_id=None,
                errors=["Something has gone wrong. Please try again later."],
            )

        return RejectProjectMembershipRequest(
            rejected_project_membership_request_id=input.project_membership_request_id,
            errors=[],
        )


class LeaveProjectInput(graphene.InputObjectType):
    project_id = graphene.ID(required=True)
    user_id = graphene.ID(required=True)


class LeaveProject(graphene.Mutation):

    class Arguments:
        input = LeaveProjectInput(required=True)

    project_id = graphene.ID()
    user_id = graphene.ID()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, input):
        _, user_id = from_global_id(input.user_id)
        _, project_id = from_global_id(input.project_id)

        project = Project.objects.get(id=project_id)
        user = User.objects.get(id=user_id)
        requesting_user = info.context.user

        try:
            project_membership = ProjectMembership.objects.get(project=project, user=user)
        except ProjectMembership.DoesNotExist:
            return LeaveProject(errors=["Project membership does not exist."], user_id=None, project_id=None)

        # Owners can't leave a project. Note that this isn't checking the requesting user.
        if project.is_owner(user):
            return LeaveProject(errors=["Project owners can't leave a project."], user_id=None, project_id=None)

        # Only the user themselves or managers/owners can remove a member
        if user != requesting_user and not project.can_edit(user=requesting_user):
            return LeaveProject(errors=["You do not have permission."], user_id=None, project_id=None)

        project_membership.is_active = False
        project_membership.save()

        return LeaveProject(user_id=input.user_id, project_id=input.project_id)


class Mutation(graphene.ObjectType):
    create_project_membership_request = CreateProjectMembershipRequest.Field()
    remove_project_membership_request = RemoveProjectMembershipRequest.Field()
    approve_project_membership_request = ApproveProjectMembershipRequest.Field()
    reject_project_membership_request = RejectProjectMembershipRequest.Field()
    leave_project = LeaveProject.Field()
