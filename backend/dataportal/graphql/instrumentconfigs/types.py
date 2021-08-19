import graphene
from graphene_django import DjangoObjectType

from ...models import Instrumentconfigs


class InstrumentconfigsType(DjangoObjectType):
    class Meta:
        model = Instrumentconfigs


class InstrumentconfigsInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    bandwidth = graphene.Decimal(required=True)
    frequency = graphene.Decimal(required=True)
    nchan = graphene.Int(required=True)
    npol = graphene.Int(required=True)
    beam = graphene.String(required=True)

    limits = Instrumentconfigs.limits
