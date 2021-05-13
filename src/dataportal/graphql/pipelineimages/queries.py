from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ...models import Pipelineimages


class PipelineimagesNode(DjangoObjectType):
    class Meta:
        model = Pipelineimages
        filter_fields = ["id", "processing", "rank"]
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    pipelineimage = relay.Node.Field(PipelineimagesNode)
    all_pipelineimages = DjangoFilterConnectionField(PipelineimagesNode, max_limit=10000)
