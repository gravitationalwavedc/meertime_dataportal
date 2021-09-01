from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Processingcollections


class ProcessingcollectionsNode(DjangoObjectType):
    class Meta:
        model = Processingcollections
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    processingcollection = relay.Node.Field(ProcessingcollectionsNode)
    all_processingcollections = DjangoFilterConnectionField(ProcessingcollectionsNode, max_limit=10000)
