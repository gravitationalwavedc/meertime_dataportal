import graphene
from graphql_jwt.decorators import login_required
from .types import *


class Query(graphene.ObjectType):
    pipelines = graphene.List(PipelinesType)
    pipelineById = graphene.Field(PipelinesType, id=graphene.Int())
    pipelinesByName = graphene.List(PipelinesType, name=graphene.String())

    @login_required
    def resolve_pipelines(cls, info, **kwargs):
        return Pipelines.objects.all()

    @login_required
    def resolve_pipelineById(cls, info, **kwargs):
        id = kwargs.get("id")
        if id is not None:
            return Pipelines.objects.get(pk=id)
        return None

    @login_required
    def resolve_pipelinesByName(cls, info, **kwargs):
        name = kwargs.get("name")
        if name is not None:
            return Pipelines.objects.filter(name=name)
        return None
