import graphene
from graphene_django import DjangoObjectType

from dataportal.models import Filterbankings


class FilterbankingsType(DjangoObjectType):
    class Meta:
        model = Filterbankings


class FilterbankingsInput(graphene.InputObjectType):
    processing_id = graphene.Int(name="processing_id", required=True)
    nbit = graphene.Int(requried=True)
    npol = graphene.Int(requried=True)
    nchan = graphene.Int(requried=True)
    tsamp = graphene.Float(requried=True)
    dm = graphene.Float(requried=True)
