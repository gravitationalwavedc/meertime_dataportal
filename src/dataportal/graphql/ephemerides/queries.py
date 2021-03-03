import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Ephemerides


class Query(graphene.ObjectType):
    ephemerides = graphene.List(EphemeridesType)

    @login_required
    def resolve_ephemerides(cls, info, **kwargs):
        return Ephemerides.objects.all()
