import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Pulsartargets


class Query(graphene.ObjectType):
    pulsartargets = graphene.List(PulsartargetsType)

    @login_required
    def resolve_pulsartargets(cls, info, **kwargs):
        return Pulsartargets.objects.all()
