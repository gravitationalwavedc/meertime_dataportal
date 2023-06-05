import graphene
from graphql_jwt.decorators import permission_required


class ObservationsInput(graphene.InputObjectType):
    target_id = graphene.Int(name="target_id", required=True)
    calibration_id = graphene.Int(name="calibration_id", required=True)
    telescope_id = graphene.Int(name="telescope_id", required=True)
    instrument_config_id = graphene.Int(name="instrument_config_id", required=True)
    project_id = graphene.Int(name="project_id", required=True)
    config = graphene.JSONString(required=True)
    utc_start = graphene.DateTime(required=True)
    duration = graphene.Float(required=True)
    nant = graphene.Int(required=True)
    nant_eff = graphene.Int(required=True)
    suspect = graphene.Boolean()
    comment = graphene.String()

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