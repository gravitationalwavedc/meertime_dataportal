import json
import graphene
from graphql_jwt.decorators import permission_required
from django_mysql.models import JSONField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from dataportal.models import (
    Template,
    Pulsar,
    Project,
)

@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class TemplateType(DjangoObjectType):
    class Meta:
        model = Template


class TemplateInput(graphene.InputObjectType):
    pulsar_name   = graphene.String(required=True)
    project_code  = graphene.String(required=True)
    band          = graphene.String(required=True)



class DeleteTemplate(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    template = graphene.Field(TemplateType)

    @classmethod
    @permission_required("dataportal.delete_template")
    def mutate(cls, self, info, id):
        _template = Template.objects.get(pk=id)
        _template.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    deleteTemplate = DeleteTemplate.Field()
