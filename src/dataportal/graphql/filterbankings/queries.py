import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Filterbankings


class Query(graphene.ObjectType):
    filterbankings = graphene.List(FilterbankingsType)

    @login_required
    def resolve_filterbankings(cls, info, **kwargs):
        return Filterbankings.objects.all()
