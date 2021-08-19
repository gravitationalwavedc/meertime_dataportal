from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ...models import Instrumentconfigs


class InstrumentconfigsNode(DjangoObjectType):
    class Meta:
        model = Instrumentconfigs
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    instrumentconfig = relay.Node.Field(InstrumentconfigsNode)
    all_instrumentconfigs = DjangoFilterConnectionField(InstrumentconfigsNode, max_limit=10000)
