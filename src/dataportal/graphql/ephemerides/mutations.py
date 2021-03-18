import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateEphemeris(graphene.Mutation):
    class Arguments:
        input = EphemeridesInput(required=True)

    ephemeris = graphene.Field(EphemeridesType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, input):
        _ephemeris, _ = Ephemerides.objects.get_or_create(**input.__dict__)
        return CreateEphemeris(ephemeris=_ephemeris)


class UpdateEphemeris(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = EphemeridesInput(required=True)

    ephemeris = graphene.Field(EphemeridesType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id, input):
        _ephemeris = Ephemerides.objects.get(pk=id)
        if _ephemeris:
            for key, val in input.__dict__.items():
                setattr(_ephemeris, key, val)
            return CreateEphemeris(ephemeris=_ephemeris)
        return CreateEphemeris(ephemeris=None)


class Mutation(graphene.ObjectType):
    create_ephemeris = CreateEphemeris.Field()
    update_ephemeris = UpdateEphemeris.Field()
