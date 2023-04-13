from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Foldings

DATETIME_FILTERS = ["exact", "isnull", "lt", "lte", "gt", "gte", "month", "year", "date"]
NUMERIC_FILTERS = ["exact", "lt", "lte", "gt", "gte"]


class FoldingsNode(DjangoObjectType):
    class Meta:
        model = Foldings
        fields = "__all__"
        filter_fields = {
            "nbin": ["exact"],
            "npol": ["exact"],
            "nchan": ["exact"],
            "processing_id": ["exact"],
            "folding_ephemeris_id": ["exact"],
            "folding_ephemeris__pulsar__id": ["exact"],
            "folding_ephemeris__pulsar__jname": ["exact"],
            "processing__observation__utc_start": DATETIME_FILTERS,
            "processing__observation__duration": NUMERIC_FILTERS,
            "processing__observation__suspect": ["exact"],
            "processing__observation__telescope__id": ["exact"],
            "processing__observation__telescope__name": ["exact"],
            "processing__observation__project__id": ["exact"],
            "processing__observation__project__code": ["exact"],
            "processing__observation__instrument_config__id": ["exact"],
            "processing__observation__instrument_config__name": ["exact"],
        }
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    folding = relay.Node.Field(FoldingsNode)
    all_foldings = DjangoFilterConnectionField(FoldingsNode, max_limit=10000)
