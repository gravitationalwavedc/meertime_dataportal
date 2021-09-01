import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Calibrations
from .types import CalibrationsInput, CalibrationsType


class CreateCalibration(graphene.Mutation):
    class Arguments:
        input = CalibrationsInput(required=True)

    calibration = graphene.Field(CalibrationsType)

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, input):
        calibration, _ = Calibrations.objects.get_or_create(**input.__dict__)
        return CreateCalibration(calibration=calibration)


class UpdateCalibration(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CalibrationsInput(required=True)

    calibration = graphene.Field(CalibrationsType)

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, id, input):
        try:
            calibration = Calibrations.objects.get(pk=id)
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
        Calibrations.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_calibration = CreateCalibration.Field()
    update_calibration = UpdateCalibration.Field()
    delete_calibration = DeleteCalibration.Field()
