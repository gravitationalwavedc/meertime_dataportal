from graphene_django import DjangoObjectType
import graphene
from ...models import Pipelineimages


class PipelineimagesType(DjangoObjectType):
    class Meta:
        model = Pipelineimages


class PipelineimagesInput(graphene.InputObjectType):
    processing_id = graphene.Int(name="processing_id", required=True)
    rank = graphene.Int(required=True)
    image_type = graphene.String(name="image_type", required=True)
    image = graphene.String(required=True)
