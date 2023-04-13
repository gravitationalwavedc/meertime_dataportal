from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Toas

DATETIME_FILTERS = ["exact", "isnull", "lt", "lte", "gt", "gte", "month", "year", "date"]
NUMERIC_FILTERS = ["exact", "lt", "lte", "gt", "gte"]


class ToasNode(DjangoObjectType):
    class Meta:
        model = Toas
        filter_fields = {
            "processing_id": ["exact"],
            "input_folding_id": ["exact"],
            "timing_ephemeris_id": ["exact"],
            "template_id": ["exact"],
            "input_folding__folding_ephemeris_id": ["exact"],
            "input_folding__folding_ephemeris__pulsar__id": ["exact"],
            "input_folding__folding_ephemeris__pulsar__jname": ["exact"],
            "processing__observation__utc_start": DATETIME_FILTERS,
            "processing__observation__duration": NUMERIC_FILTERS,
            "processing__observation__suspect": ["exact"],
            "processing__observation__telescope__id": ["exact"],
            "processing__observation__telescope__name": ["exact"],
            "processing__observation__project__id": ["exact"],
            "processing__observation__project__code": ["exact"],
            "processing__observation__instrument_config__id": ["exact"],
            "processing__observation__instrument_config__name": ["exact"],
            "processing__pipeline__id": ["exact"],
            "processing__pipeline__name": ["exact"],
        }
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    toa = relay.Node.Field(ToasNode)
    all_toas = DjangoFilterConnectionField(ToasNode, max_limit=10000)
