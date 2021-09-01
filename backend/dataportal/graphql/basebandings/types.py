import graphene
from graphene_django import DjangoObjectType

from dataportal.models import Basebandings


class BasebandingsType(DjangoObjectType):
    class Meta:
        model = Basebandings


class BasebandingsInput(graphene.InputObjectType):
    processing_id = graphene.Int(name="processing_id", required=True)
