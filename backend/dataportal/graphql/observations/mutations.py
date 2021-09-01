import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Observations
from .types import ObservationsInput, ObservationsType


class CreateObservation(graphene.Mutation):
    class Arguments:
        input = ObservationsInput(required=True)

    observation = graphene.Field(ObservationsType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, input=None):
        observation, _ = Observations.objects.get_or_create(**input.__dict__)
        return CreateObservation(observation=observation)


class UpdateObservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ObservationsInput(required=True)

    observation = graphene.Field(ObservationsType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, id, input=None):
        try:
            observation = Observations.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(observation, key, val)
            observation.save()
            return UpdateObservation(observation=observation)
        except:
            return UpdateObservation(observation=None)


class DeleteObservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, id):
        Observations.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_observation = CreateObservation.Field()
    update_observation = UpdateObservation.Field()
    delete_observation = DeleteObservation.Field()
