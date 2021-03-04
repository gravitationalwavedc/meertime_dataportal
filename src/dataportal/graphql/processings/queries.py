from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ..jsonfield_filter import JSONFieldFilter
from ...models import Processings


class ProcessingsNode(DjangoObjectType):
    class Meta:
        model = Processings
        filterset_class = JSONFieldFilter
        interfaces = (relay.Node,)


class Query(ObjectType):
    processing = relay.Node.Field(ProcessingsNode)
    all_processings = DjangoFilterConnectionField(ProcessingsNode)
