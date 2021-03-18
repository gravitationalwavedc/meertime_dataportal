import graphene
from graphene_django import DjangoObjectType

from ...models import Calibrations


class CalibrationsType(DjangoObjectType):
    class Meta:
        model = Calibrations


class CalibrationsInput(graphene.InputObjectType):
    type = graphene.String(required=True)
    location = graphene.String(required=True)
