import graphene
from graphql_jwt.decorators import permission_required
from decimal import Decimal

from dataportal.models import Ephemerides
from .types import EphemeridesInput, EphemeridesType


class CreateEphemeris(graphene.Mutation):
    class Arguments:
        input = EphemeridesInput(required=True)

    ephemeris = graphene.Field(EphemeridesType)

    @classmethod
    @permission_required("dataportal.add_ephemerides")
    def mutate(cls, self, info, input):
        # santize the the decimal values due to Django bug
        for field, limits in EphemeridesInput.limits.items():
            deci_str = "1.".ljust(limits["deci"] + 2, "0")
            input.__dict__[field] = input.__dict__[field].quantize(Decimal(deci_str))
        _ephemeris, _ = Ephemerides.objects.get_or_create(**input.__dict__)
        return CreateEphemeris(ephemeris=_ephemeris)


class UpdateEphemeris(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = EphemeridesInput(required=True)

    ephemeris = graphene.Field(EphemeridesType)

    @classmethod
    @permission_required("dataportal.add_ephemerides")
    def mutate(cls, self, info, id, input):
        _ephemeris = Ephemerides.objects.get(pk=id)
        if _ephemeris:
            for key, val in input.__dict__.items():
                limits = EphemeridesInput.limits.get(key)
                if limits:
                    deci_str = "1.".ljust(limits["deci"] + 2, "0")
                    val = val.quantize(Decimal(deci_str))
                setattr(_ephemeris, key, val)
            _ephemeris.save()
            return UpdateEphemeris(ephemeris=_ephemeris)
        return UpdateEphemeris(ephemeris=None)


class DeleteEphemeris(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    ephemeris = graphene.Field(EphemeridesType)

    @classmethod
    @permission_required("dataportal.add_ephemerides")
    def mutate(cls, self, info, id):
        _ephemeris = Ephemerides.objects.get(pk=id)
        _ephemeris.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_ephemeris = CreateEphemeris.Field()
    update_ephemeris = UpdateEphemeris.Field()
    delete_ephemeris = DeleteEphemeris.Field()
