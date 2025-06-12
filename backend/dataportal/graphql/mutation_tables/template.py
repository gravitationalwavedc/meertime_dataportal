import graphene
from django.contrib.postgres.fields import JSONField
from graphene_django.converter import convert_django_field

from dataportal.graphql.queries import TemplateNode
from dataportal.models import Template
from user_manage.graphql.decorators import permission_required


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class TemplateInput(graphene.InputObjectType):
    pulsar_name = graphene.String(required=True)
    project_code = graphene.String(required=True)
    band = graphene.String(required=True)


class DeleteTemplate(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    template = graphene.Field(TemplateNode)

    @permission_required("dataportal.delete_template")
    def mutate(root, info, id):
        _template = Template.objects.get(pk=id)
        _template.delete()
        return DeleteTemplate(ok=True)


class Mutation(graphene.ObjectType):
    deleteTemplate = DeleteTemplate.Field()
