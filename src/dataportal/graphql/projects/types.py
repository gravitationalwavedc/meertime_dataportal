from graphene import String
from django.db.models.fields import DurationField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from ...models import Projects


@convert_django_field.register(DurationField)
def convert_duration_field_to_string(field, registry=None):
    return String()


class ProjectsType(DjangoObjectType):
    class Meta:
        model = Projects
