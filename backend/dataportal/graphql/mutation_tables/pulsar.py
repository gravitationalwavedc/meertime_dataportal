import graphene
from graphql_jwt.decorators import permission_required
from graphene_django import DjangoObjectType

from dataportal.models import Pulsar

class PulsarType(DjangoObjectType):
    class Meta:
        model = Pulsar


class PulsarsInput(graphene.InputObjectType):
    jname = graphene.String(required=True)
    state = graphene.String(required=True)
    comment = graphene.String(required=True)

class CreatePulsar(graphene.Mutation):
    class Arguments:
        input = PulsarsInput(required=True)

    pulsar = graphene.Field(PulsarType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, input):
        pulsar, _ = Pulsar.objects.get_or_create(**input.__dict__)
        return CreatePulsar(pulsar=pulsar)


class UpdatePulsar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PulsarsInput(required=True)

    pulsar = graphene.Field(PulsarType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id, input):
        try:
            pulsar = Pulsar.objects.get(pk=id)
            for key, value in input.__dict__.items():
                setattr(pulsar, key, value)
            pulsar.save()
            return UpdatePulsar(pulsar=pulsar)
        except:
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