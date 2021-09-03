from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Sessions

DATETIME_FILTERS = ['exact', 'isnull', 'lt', 'lte', 'gt', 'gte', 'month', 'year', 'date']


class SessionsNode(DjangoObjectType):
    class Meta:
        model = Sessions
        fields = "__all__"
        filter_fields = {
            "telescope__id": ["exact"],
            "telescope__name": ["exact"],
            "start": DATETIME_FILTERS,
            "end": DATETIME_FILTERS,
        }
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    session = relay.Node.Field(SessionsNode)
    all_sessions = DjangoFilterConnectionField(SessionsNode, max_limit=10000)
