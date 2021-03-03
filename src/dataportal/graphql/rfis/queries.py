import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Rfis


class Query(graphene.ObjectType):
    rfis = graphene.List(RfisType)

    @login_required
    def resolve_rfis(cls, info, **kwargs):
        return Rfis.objects.all()
