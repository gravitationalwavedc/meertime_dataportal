import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Processings


class Query(graphene.ObjectType):
    processings = graphene.List(ProcessingsType)

    @login_required
    def resolve_processings(cls, info, **kwargs):
        return Processings.objects.all()
