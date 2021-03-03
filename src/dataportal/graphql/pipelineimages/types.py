from graphene_django import DjangoObjectType

from ...models import Pipelineimages


class PipelineimagesType(DjangoObjectType):
    class Meta:
        model = Pipelineimages
