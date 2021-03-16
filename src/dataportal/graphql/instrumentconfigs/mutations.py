import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateInstrumentconfig(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        bandwidth = graphene.Decimal()
        frequency = graphene.Decimal()
        nchan = graphene.Int()
        npol = graphene.Int()
        beam = graphene.String()

    instrumentconfig = graphene.Field(InstrumentconfigsType)

    @classmethod
    @permission_required("dataportal.add_instrumentconfigs")
    def mutate(cls, self, info, name, bandwidth, frequency, nchan, npol, beam):
        _instrumentconfig, _ = Instrumentconfigs.objects.get_or_create(
            name=name, bandwidth=bandwidth, frequency=frequency, nchan=nchan, npol=npol, beam=beam
        )
        return CreateInstrumentconfig(instrumentconfig=_instrumentconfig)


class Mutation(graphene.ObjectType):
    create_instrumentconfig = CreateInstrumentconfig.Field()
