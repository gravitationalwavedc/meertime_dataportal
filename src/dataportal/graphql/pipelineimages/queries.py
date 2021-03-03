import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Pipelineimages


class Query(graphene.ObjectType):
    pipelineimages = graphene.List(PipelineimagesType)

    @login_required
    def resolve_pipelineimages(cls, info, **kwargs):
        return Pipelineimages.objects.all()
