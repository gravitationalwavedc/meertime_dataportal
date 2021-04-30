from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

# from ..jsonfield_filter import JSONFieldFilter
from ...models import Processings

DATETIME_FILTERS = ['exact', 'isnull', 'lt', 'lte', 'gt', 'gte', 'month', 'year', 'date']
NUMERIC_FILTERS = ['exact', 'lt', 'lte', 'gt', 'gte']


class ProcessingsNode(DjangoObjectType):
    class Meta:
        model = Processings
        fields = "__all__"
        filter_fields = {
            "observation_id": ["exact"],
            "pipeline_id": ["exact"],
            "parent_id": ["exact"],
            "embargo_end": DATETIME_FILTERS,
            "observation__utc_start": DATETIME_FILTERS,
            "observation__duration": NUMERIC_FILTERS,
            "observation__suspect": ["exact"],
            "observation__telescope__id": ["exact"],
            "observation__telescope__name": ["exact"],
            "observation__target__id": ["exact"],
            "observation__target__name": ["exact"],
            "observation__project__id": ["exact"],
            "observation__project__code": ["exact"],
            "observation__instrument_config__id": ["exact"],
            "observation__instrument_config__name": ["exact"],
        }
        # filterset_class = JSONFieldFilter
        interfaces = (relay.Node,)


class Query(ObjectType):
    processing = relay.Node.Field(ProcessingsNode)
    all_processings = DjangoFilterConnectionField(ProcessingsNode)
