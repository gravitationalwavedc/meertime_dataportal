import graphene
from django.contrib.postgres.fields import JSONField
from graphene_django.converter import convert_django_field
from user_manage.graphql.decorators import permission_required

from dataportal.graphql.queries import PipelineImageNode
from dataportal.models import PipelineImage


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class PipelineImageInput(graphene.InputObjectType):
    pulsar_name = graphene.String(required=True)
    project_code = graphene.String(required=True)
    band = graphene.String(required=True)


class DeletePipelineImage(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    pipeline_image = graphene.Field(PipelineImageNode)

    @permission_required("dataportal.delete_pipeline_image")
    def mutate(root, info, id):
        _pipeline_image = PipelineImage.objects.get(pk=id)
        _pipeline_image.delete()
        return DeletePipelineImage(ok=True)


class Mutation(graphene.ObjectType):
    deletePipelineImage = DeletePipelineImage.Field()
