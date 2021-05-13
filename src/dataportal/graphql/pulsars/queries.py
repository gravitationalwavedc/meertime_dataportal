from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Pulsars


class PulsarsNode(DjangoObjectType):
    class Meta:
        model = Pulsars
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    pulsar = relay.Node.Field(PulsarsNode)
    all_pulsars = DjangoFilterConnectionField(PulsarsNode, max_limit=10000)
