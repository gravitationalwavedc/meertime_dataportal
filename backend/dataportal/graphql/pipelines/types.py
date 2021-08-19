import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from django_mysql.models import JSONField

from ...models import Pipelines


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


class PipelinesType(DjangoObjectType):
    class Meta:
        model = Pipelines


class PipelinesInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    revision = graphene.String(required=True)
    created_at = graphene.DateTime(required=True, name="created_at")
    created_by = graphene.String(required=True, name="created_by")
    configuration = graphene.JSONString(required=True)
