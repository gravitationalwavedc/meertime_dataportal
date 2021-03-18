import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateObservation(graphene.Mutation):
    class Arguments:
        input = ObservationsInput(required=True)

    observation = graphene.Field(ObservationsType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, input=None):
        _observation, _ = Observations.objects.get_or_create(**input.__dict__)
        return CreateObservation(observation=_observation)


class UpdateObservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ObservationsInput(required=True)

    observation = graphene.Field(ObservationsType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, id, input=None):
        _observation = Observations.objects.get(pk=id)
        if _observation:
            for key, val in input.__dict__.items():
                setattr(_observation, key, val)
            return CreateObservation(observation=_observation)
        return CreateObservation(observation=None)


class Mutation(graphene.ObjectType):
    create_observation = CreateObservation.Field()
    update_observation = UpdateObservation.Field()
