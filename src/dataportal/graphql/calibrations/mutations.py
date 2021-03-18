import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateCalibration(graphene.Mutation):
    class Arguments:
        input = CalibrationsInput(required=True)

    calibration = graphene.Field(CalibrationsType)

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, input):
        _calibration, _ = Calibrations.objects.get_or_create(**input.__dict__)
        return CreateCalibration(calibration=_calibration)


class UpdateCalibration(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CalibrationsInput(required=True)

    calibration = graphene.Field(CalibrationsType)

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, id, input):
        _calibration, _ = Calibrations.objects.get(id)
        if _calibration:
            for key, val in input.__dict__.items():
                setattr(_calibration, key, val)
            _calibration.save()
            return UpdateCalibration(calibration=_calibration)
        return UpdateCalibration(calibration=None)


class Mutation(graphene.ObjectType):
    create_calibration = CreateCalibration.Field()
    update_calibration = UpdateCalibration.Field()
