from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ...models import Pulsaraliases


class PulsaraliasesNode(DjangoObjectType):
    class Meta:
        model = Pulsaraliases
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    pulsaralias = relay.Node.Field(PulsaraliasesNode)
    all_pulsaraliases = DjangoFilterConnectionField(PulsaraliasesNode)
