import graphene
from graphql_jwt.decorators import permission_required

from dataportal.graphql.queries import PulsarNode
from dataportal.models import Pulsar


class PulsarsInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    comment = graphene.String()


class CreatePulsar(graphene.Mutation):
    class Arguments:
        input = PulsarsInput()

    pulsar = graphene.Field(PulsarNode)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, input):
        pulsar, _ = Pulsar.objects.get_or_create(
            name=input.name,
            defaults={
                "comment": input.comment,
            },
        )
        return CreatePulsar(pulsar=pulsar)


class UpdatePulsar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PulsarsInput(required=True)

    pulsar = graphene.Field(PulsarNode)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id, input):
        try:
            pulsar = Pulsar.objects.get(pk=id)
            for key, value in input.__dict__.items():
                setattr(pulsar, key, value)
            pulsar.save()
            return UpdatePulsar(pulsar=pulsar)
        except Exception:
            return UpdatePulsar(pulsar=None)


class DeletePulsar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id):
        Pulsar.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    createPulsar = CreatePulsar.Field()
    updatePulsar = UpdatePulsar.Field()
    deletePulsar = DeletePulsar.Field()
