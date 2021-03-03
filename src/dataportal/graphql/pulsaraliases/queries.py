import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Pulsaraliases


class Query(graphene.ObjectType):
    pulsaraliases = graphene.List(PulsaraliasesType)

    @login_required
    def resolve_pulsaraliases(cls, info, **kwargs):
        return Pulsaraliases.objects.all()
