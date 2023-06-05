import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Pulsar, Observation

DATETIME_FILTERS = ["exact", "isnull", "lt", "lte", "gt", "gte", "month", "year", "date"]
NUMERIC_FILTERS = ["exact", "lt", "lte", "gt", "gte"]

class Queries:
    pass


class PulsarsNode(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = "__all__"
        filter_fields = "__all__"

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ObservationsNode(DjangoObjectType):
    class Meta:
        model = Observation
        fields = "__all__"
        filter_fields = {
            "utc_start": DATETIME_FILTERS,
            "duration": NUMERIC_FILTERS,
            "suspect": ["exact"],
            "telescope__id": ["exact"],
            "telescope__name": ["exact"],
            "target__id": ["exact"],
            "target__name": ["exact"],
            "project__id": ["exact"],
            "project__code": ["exact"],
            "instrument_config__id": ["exact"],
            "instrument_config__name": ["exact"],
        }
        # filterset_class = JSONFieldFilter
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(graphene.ObjectType):
    pulsar = graphene.Field(
        PulsarsNode,
        name=graphene.String(required=True),
    )
    all_observations = DjangoFilterConnectionField(ObservationsNode, max_limit=10000)

    observation = relay.Node.Field(ObservationsNode)
    all_observations = DjangoFilterConnectionField(ObservationsNode, max_limit=10000)

