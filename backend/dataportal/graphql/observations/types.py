import graphene
from django_mysql.models import JSONField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from dataportal.models import Observations


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class ObservationsType(DjangoObjectType):
    class Meta:
        model = Observations


class ObservationsInput(graphene.InputObjectType):
    target_id = graphene.Int(name="target_id", required=True)
    calibration_id = graphene.Int(name="calibration_id", required=True)
    telescope_id = graphene.Int(name="telescope_id", required=True)
    instrument_config_id = graphene.Int(name="instrument_config_id", required=True)
    project_id = graphene.Int(name="project_id", required=True)
    config = graphene.JSONString(required=True)
    utc_start = graphene.DateTime(required=True)
    duration = graphene.Float(required=True)
    nant = graphene.Int(required=True)
    nant_eff = graphene.Int(required=True)
    suspect = graphene.Boolean()
    comment = graphene.String()
