import graphene
from graphene_django import DjangoObjectType

from dataportal.models import Pulsar


class PulsarsType(DjangoObjectType):
    class Meta:
        model = Pulsar


class PulsarsInput(graphene.InputObjectType):
    jname = graphene.String(required=True)
    state = graphene.String(required=True)
    comment = graphene.String(required=True)
