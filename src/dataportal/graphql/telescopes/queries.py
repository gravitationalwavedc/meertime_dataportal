import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Telescopes


class Query(graphene.ObjectType):
    telescopes = graphene.List(TelescopesType)

    @login_required
    def resolve_telescopes(cls, info, **kwargs):
        return Telescopes.objects.all()
