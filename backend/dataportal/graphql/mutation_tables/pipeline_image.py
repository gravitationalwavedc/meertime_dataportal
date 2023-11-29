import json
import graphene
from graphql_jwt.decorators import permission_required
from django.contrib.postgres.fields import JSONField
from graphene_django.converter import convert_django_field

from dataportal.models import (
    PipelineImage,
)
from dataportal.graphql.queries import PipelineImageNode


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class PipelineImageInput(graphene.InputObjectType):
    pulsar_name   = graphene.String(required=True)
    project_code  = graphene.String(required=True)
    band          = graphene.String(required=True)



class DeletePipelineImage(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    pipeline_image = graphene.Field(PipelineImageNode)

    @classmethod
    @permission_required("dataportal.delete_pipeline_image")
    def mutate(cls, self, info, id):
        _pipeline_image = PipelineImage.objects.get(pk=id)
        _pipeline_image.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    deletePipelineImage = DeletePipelineImage.Field()
