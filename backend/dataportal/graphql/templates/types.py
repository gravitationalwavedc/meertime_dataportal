import graphene
from graphene_django import DjangoObjectType

from dataportal.models import Templates


class TemplatesType(DjangoObjectType):
    class Meta:
        model = Templates


class TemplatesInput(graphene.InputObjectType):
    pulsar_id = graphene.Int(name="pulsar_id", required=True)
    frequency = graphene.Float(required=True)
    bandwidth = graphene.Float(required=True)
    created_at = graphene.DateTime(name="created_at", required=True)
    created_by = graphene.String(name="created_by", required=True)
    location = graphene.String(required=True)
    method = graphene.String(required=True)
    type = graphene.String(required=True)
    comment = graphene.String(required=True)
