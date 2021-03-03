import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Basebandings


class Query(graphene.ObjectType):
    basebandings = graphene.List(BasebandingsType)

    @login_required
    def resolve_basebandings(cls, info, **kwargs):
        return Basebandings.objects.all()
