from graphene import relay, ObjectType, List
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

# from .types import *
from dataportal.models import Pulsar


class PulsarsNode(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = "__all__"
        filter_fields = "__all__"

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(ObjectType):
    pulsars = List(PulsarsNode)

    def resolve_pulsars(self, info, **kwargs):
        return Pulsar.objects.all()
