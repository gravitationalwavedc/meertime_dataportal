import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreatePulsar(graphene.Mutation):
    class Arguments:
        input = PulsarsInput(required=True)

    pulsar = graphene.Field(PulsarsType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, input):
        _pulsar, _ = Pulsars.objects.get_or_create(**input.__dict__)
        return CreatePulsar(pulsar=_pulsar)


class UpdatePulsar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PulsarsInput(required=True)

    pulsar = graphene.Field(PulsarsType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id, input):
        _pulsar = Pulsars.objects.get(pk=id)
        if _pulsar:
            for key, value in input.__dict__.items():
                setattr(_pulsar, key, value)
            _pulsar.save()
            return UpdatePulsar(pulsar=_pulsar)
        return UpdatePulsar(pulsar=None)


class DeletePulsar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    pulsar = graphene.Field(PulsarsType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id):
        _pulsar = Pulsars.objects.get(pk=id)
        _pulsar.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_pulsar = CreatePulsar.Field()
    update_pulsar = UpdatePulsar.Field()
    delete_pulsar = DeletePulsar.Field()
