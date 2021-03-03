from graphene_django import DjangoObjectType

from ...models import Calibrations


class CalibrationsType(DjangoObjectType):
    class Meta:
        model = Calibrations
