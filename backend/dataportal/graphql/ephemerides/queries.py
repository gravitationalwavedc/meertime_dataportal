from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Ephemerides

NUMERIC_FILTERS = ['exact', 'lt', 'lte', 'gt', 'gte']


class EphemeridesNode(DjangoObjectType):
    class Meta:
        model = Ephemerides
        filter_fields = {"pulsar__id": ["exact"], "p0": NUMERIC_FILTERS, "dm": NUMERIC_FILTERS, "rm": NUMERIC_FILTERS}
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    ephemeris = relay.Node.Field(EphemeridesNode)
    all_ephemerides = DjangoFilterConnectionField(EphemeridesNode, max_limit=10000)
