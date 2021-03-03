import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreatePulsar(graphene.Mutation):
    class Arguments:
        jname = graphene.String(required=True)
        state = graphene.String(required=True)
        comment = graphene.String(required=True)

    pulsar = graphene.Field(PulsarsType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, jname, state, comment):
        _pulsar, _ = Pulsars.objects.get_or_create(jname=jname, state=state, comment=comment)
        return CreatePulsar(pulsar=_pulsar)


class UpdatePulsar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        jname = graphene.String(required=True)
        state = graphene.String(required=True)
        comment = graphene.String(required=True)

    pulsar = graphene.Field(PulsarsType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id, jname, state, comment):
        ok = False
        _pulsar = Pulsars.objects.get(pk=id)
        if _pulsar:
            _pulsar.jname = jname
            _pulsar.state = state
            _pulsar.comment = comment
            return UpdatePulsar(pulsar=_pulsar)
        return UpdatePulsar(pulsar=None)


class Mutation(graphene.ObjectType):
    create_pulsar = CreatePulsar.Field()
    update_pulsar = UpdatePulsar.Field()
