from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Pipelinefiles


class PipelinefilesNode(DjangoObjectType):
    class Meta:
        model = Pipelinefiles
        filter_fields = ["id", "processing", "file_type"]
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    pipelinefile = relay.Node.Field(PipelinefilesNode)
    all_pipelinefiles = DjangoFilterConnectionField(PipelinefilesNode, max_limit=10000)
