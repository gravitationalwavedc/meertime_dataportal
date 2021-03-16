import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateCalibration(graphene.Mutation):
    class Arguments:
        type = graphene.String()
        location = graphene.String()

    calibration = graphene.Field(CalibrationsType)

    @classmethod
    @permission_required("dataportal.add_calibrations")
    def mutate(cls, self, info, type, location):
        _calibration, _ = Calibrations.objects.get_or_create(calibration_type=type, location=location)
        return CreateCalibration(calibration=_calibration)


class Mutation(graphene.ObjectType):
    create_calibration = CreateCalibration.Field()
