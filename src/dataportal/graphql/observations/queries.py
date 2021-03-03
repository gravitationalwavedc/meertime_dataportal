import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Observations


class Query(graphene.ObjectType):
    observations = graphene.List(ObservationsType)

    @login_required
    def resolve_observations(cls, info, **kwargs):
        return Observations.objects.all()
