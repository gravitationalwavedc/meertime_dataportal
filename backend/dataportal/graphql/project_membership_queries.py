from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from user_manage.graphql.decorators import login_required
from dataportal.models import ProjectMembershipRequest, ProjectMembership


class ProjectMembershipRequestNode(DjangoObjectType):

    class Meta:
        model = ProjectMembershipRequest
        interfaces = (relay.Node,)
        fields = ["user", "project", "status", "requested_at", "message"]


class ProjectMembershipNode(DjangoObjectType):

    class Meta:
        model = ProjectMembership
        interfaces = (relay.Node,)
        fields = ["user", "project", "role", "joined_at", "approved_by"]


class ProjectMembershipRequestConnection(relay.Connection):

    class Meta:
        node = ProjectMembershipRequestNode


class ProjectMembershipConnection(relay.Connection):

    class Meta:
        node = ProjectMembershipNode


class Query(ObjectType):
    project_membership_request = relay.Node.Field(ProjectMembershipRequestNode)
    project_membership_requests = relay.ConnectionField(ProjectMembershipRequestConnection)
    project_membership_requests_for_approval = relay.ConnectionField(ProjectMembershipRequestConnection)
    project_memberships = relay.ConnectionField(ProjectMembershipConnection)

    @login_required
    def resolve_project_membership_requests(self, info, **kwargs):
        return ProjectMembershipRequest.user_requests(info.context.user)

    @login_required
    def resolve_project_membership_requests_for_approval(self, info, **kwargs):
        return ProjectMembershipRequest.membership_approval_requests(info.context.user)

    @login_required
    def resolve_project_memberships(self, info, **kwargs):
        return ProjectMembership.objects.filter(user=info.context.user, is_active=True)
