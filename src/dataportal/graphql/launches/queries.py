import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Launches


class Query(graphene.ObjectType):
    launches = graphene.List(LaunchesType)

    @login_required
    def resolve_launches(cls, info, **kwargs):
        return Launches.objects.all()
