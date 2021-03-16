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
        _observation, _ = Observations.objects.get_or_create(
            target_id=input.target_id,
            calibration_id=input.calibration_id,
            telescope_id=input.telescope_id,
            instrument_config_id=input.instrument_config_id,
            project_id=input.project_id,
            config=input.config,
            utc_start=input.utc_start,
            duration=input.duration,
            nant=input.nant,
            nant_eff=input.nant_eff,
            suspect=input.suspect,
            comment=input.comment,
        )
        return CreateObservation(observation=_observation)


class Mutation(graphene.ObjectType):
    create_observation = CreateObservation.Field()
