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
    createdAt = graphene.DateTime(required=True)
    createdBy = graphene.String(required=True)
    configuration = graphene.String(required=True)
