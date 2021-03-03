import graphene
from graphql_jwt.decorators import login_required
from .types import *


class Query(graphene.ObjectType):
    targets = graphene.List(TargetsType)
    targetById = graphene.Field(TargetsType, id=graphene.Int())
    targetsByName = graphene.List(TargetsType, name=graphene.String())

    @login_required
    def resolve_targets(cls, info, **kwargs):
        return Targets.objects.all()

    @login_required
    def resolve_targetById(cls, info, **kwargs):
        id = kwargs.get("id")
        if id is not None:
            return Targets.objects.get(pk=id)
        return None

    @login_required
    def resolve_targetsByName(cls, info, **kwargs):
        name = kwargs.get("name")
        if name is not None:
            return Targets.objects.filter(name=name)
        return None
