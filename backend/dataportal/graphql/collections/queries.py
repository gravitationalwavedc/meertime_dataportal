from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Collections


class CollectionsNode(DjangoObjectType):
    class Meta:
        model = Collections
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    collection = relay.Node.Field(CollectionsNode)
    all_collections = DjangoFilterConnectionField(CollectionsNode, max_limit=10000)
