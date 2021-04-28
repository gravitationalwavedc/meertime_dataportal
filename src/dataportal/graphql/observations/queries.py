from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ..jsonfield_filter import JSONFieldFilter
from ...models import Observations


class ObservationsNode(DjangoObjectType):
    class Meta:
        model = Observations
        fields = "__all__"
        filter_fields = [
            "utc_start",
            "duration",
            "suspect",
            "telescope__id",
            "telescope__name",
            "target__id",
            "target__name",
            "project__id",
            "project__code",
            "instrument_config__id",
            "instrument_config__name",
        ]
        # filterset_class = JSONFieldFilter
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    observation = relay.Node.Field(ObservationsNode)
    all_observations = DjangoFilterConnectionField(ObservationsNode)
