import graphene
from graphene_django import DjangoObjectType

from ...models import Pulsars


class PulsarsType(DjangoObjectType):
    class Meta:
        model = Pulsars


class PulsarsInput(graphene.InputObjectType):
    jname = graphene.String(required=True)
    state = graphene.String(required=True)
    comment = graphene.String(required=True)
