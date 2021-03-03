import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Foldings


class Query(graphene.ObjectType):
    foldings = graphene.List(FoldingsType)

    @login_required
    def resolve_foldings(cls, info, **kwargs):
        return Foldings.objects.all()
