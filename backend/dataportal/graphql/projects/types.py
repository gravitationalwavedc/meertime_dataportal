import graphene
from django.db.models.fields import DurationField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from dataportal.models import Projects


@convert_django_field.register(DurationField)
def convert_duration_field_to_string(field, registry=None):
    return graphene.String()


class ProjectsType(DjangoObjectType):
    class Meta:
        model = Projects


class ProjectsInput(graphene.InputObjectType):
    program_id = graphene.Int(name="program_id", required="True")
    code = graphene.String()
    short = graphene.String()
    embargo_period = graphene.Int()
    description = graphene.String()
