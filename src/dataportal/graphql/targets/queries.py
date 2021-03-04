from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ..jsonfield_filter import JSONFieldFilter
from ...models import Targets


class TargetsNode(DjangoObjectType):
    class Meta:
        model = Targets
        filterset_class = JSONFieldFilter
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    target = relay.Node.Field(TargetsNode)
    all_targets = DjangoFilterConnectionField(TargetsNode)
