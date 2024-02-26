import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Calibration
from dataportal.graphql.queries import CalibrationNode


class CalibrationInput(graphene.InputObjectType):
    schedule_block_id = graphene.String()
    calibration_type = graphene.String(required=True)
    location = graphene.String()


class CreateCalibration(graphene.Mutation):
    class Arguments:
        input = CalibrationInput()

    calibration = graphene.Field(CalibrationNode)

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, input):
        calibration, _ = Calibration.objects.get_or_create(**input.__dict__)
        return CreateCalibration(calibration=calibration)


class UpdateCalibration(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CalibrationInput(required=True)

    calibration = graphene.Field(CalibrationNode)

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, id, input):
        try:
            calibration = Calibration.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(calibration, key, val)
            calibration.save()
            return UpdateCalibration(calibration=calibration)
        except:
            return UpdateCalibration(calibration=None)


class DeleteCalibration(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, id):
        Calibration.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    createCalibration = CreateCalibration.Field()
    updateCalibration = UpdateCalibration.Field()
    deleteCalibration = DeleteCalibration.Field()
