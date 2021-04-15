from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from ...models import Ephemerides


class EphemeridesNode(DjangoObjectType):
    class Meta:
        model = Ephemerides
        filter_fields = ["pulsar", "p0", "dm", "rm"]
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    ephemeris = relay.Node.Field(EphemeridesNode)
    all_ephemerides = DjangoFilterConnectionField(EphemeridesNode)
