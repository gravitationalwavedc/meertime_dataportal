from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Rfis


class RfisNode(DjangoObjectType):
    class Meta:
        model = Rfis
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    rfi = relay.Node.Field(RfisNode)
    all_rfis = DjangoFilterConnectionField(RfisNode, max_limit=10000)
