from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Programs


class ProgramsNode(DjangoObjectType):
    class Meta:
        model = Programs
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    program = relay.Node.Field(ProgramsNode)
    all_programs = DjangoFilterConnectionField(ProgramsNode, max_limit=10000)
