from graphene_django import DjangoObjectType
import graphene

from dataportal.models import Pipelinefiles


class PipelinefilesType(DjangoObjectType):
    class Meta:
        model = Pipelinefiles


class PipelinefilesInput(graphene.InputObjectType):
    file = graphene.String(required=True)
    file_name = graphene.String(name="file_name", required=True)
    file_type = graphene.String(name="file_type", required=True)
    processing_id = graphene.Int(name="processing_id", required=True)
