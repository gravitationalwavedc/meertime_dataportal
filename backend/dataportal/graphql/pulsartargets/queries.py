from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Pulsartargets


class PulsartargetsNode(DjangoObjectType):
    class Meta:
        model = Pulsartargets
        filter_fields = [
            "target__id",
            "target__name",
            "pulsar__id",
            "pulsar__jname",
        ]
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    pulsartarget = relay.Node.Field(PulsartargetsNode)
    all_pulsartargets = DjangoFilterConnectionField(PulsartargetsNode, max_limit=10000)
