import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Calibrations


class Query(graphene.ObjectType):
    calibrations = graphene.List(CalibrationsType)

    @login_required
    def resolve_calibrations(cls, info, **kwargs):
        return Calibrations.objects.all()
