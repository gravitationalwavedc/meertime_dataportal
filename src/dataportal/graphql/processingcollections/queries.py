import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Processingcollections


class Query(graphene.ObjectType):
    processingcollections = graphene.List(ProcessingcollectionsType)

    @login_required
    def resolve_processingcollections(cls, info, **kwargs):
        return Processingcollections.objects.all()
