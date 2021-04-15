import graphene
from django_mysql.models import JSONField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from ...models import Ephemerides


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class EphemeridesType(DjangoObjectType):
    class Meta:
        model = Ephemerides


class EphemeridesInput(graphene.InputObjectType):
    pulsar_id = graphene.Int(name="pulsar_id", required=True)
    created_at = graphene.DateTime(name="created_at", required=True)
    created_by = graphene.String(name="created_by", required=True)
    ephemeris = graphene.JSONString(required=True)
    p0 = graphene.Float(required=True)
    dm = graphene.Float(required=True)
    rm = graphene.Float(required=True)
    comment = graphene.String(required=True)
    valid_from = graphene.DateTime(name="valid_from", required=True)
    valid_to = graphene.DateTime(name="valid_to", required=True)
