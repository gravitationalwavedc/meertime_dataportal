import graphene
from django_mysql.models import JSONField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from dataportal.models import Toas


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class ToasType(DjangoObjectType):
    class Meta:
        model = Toas


class ToasInput(graphene.InputObjectType):
    processing_id = graphene.Int(name="processing_id", required=True)
    input_folding_id = graphene.Int(name="input_folding_id", required=True)
    timing_ephemeris_id = graphene.Int(name="timing_ephemeris_id", required=True)
    template_id = graphene.Int(name="template_id", required=True)
    flags = graphene.JSONString(required=True)
    frequency = graphene.Float(required=True)
    mjd = graphene.String(required=True)
    site = graphene.String(required=True)
    uncertainty = graphene.Float(required=True)
    quality = graphene.String(required=True)
    comment = graphene.String(required=True)
