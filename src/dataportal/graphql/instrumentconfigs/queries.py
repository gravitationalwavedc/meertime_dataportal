import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Instrumentconfigs


class Query(graphene.ObjectType):
    instrumentconfigs = graphene.List(InstrumentconfigsType)

    @login_required
    def resolve_instrumentconfigs(cls, info, **kwargs):
        return Instrumentconfigs.objects.all()
