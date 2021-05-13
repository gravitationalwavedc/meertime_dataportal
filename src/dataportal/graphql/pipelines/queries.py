from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ..jsonfield_filter import JSONFieldFilter
from ...models import Pipelines


class PipelinesNode(DjangoObjectType):
    class Meta:
        model = Pipelines
        fields = "__all__"
        filter_fields = ["name"]
        # filterset_class = JSONFieldFilter
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    pipeline = relay.Node.Field(PipelinesNode)
    all_pipelines = DjangoFilterConnectionField(PipelinesNode, max_limit=10000)
