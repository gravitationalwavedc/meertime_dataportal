import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Toas


class Query(graphene.ObjectType):
    toas = graphene.List(ToasType)

    @login_required
    def resolve_toas(cls, info, **kwargs):
        return Toas.objects.all()
