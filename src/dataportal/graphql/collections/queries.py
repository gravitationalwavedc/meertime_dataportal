import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Collections


class Query(graphene.ObjectType):
    collections = graphene.List(CollectionsType)

    @login_required
    def resolve_collections(cls, info, **kwargs):
        return Collections.objects.all()
