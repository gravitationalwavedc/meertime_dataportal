import graphene
from graphene_django import DjangoObjectType

from dataportal.models import Foldings


class FoldingsType(DjangoObjectType):
    class Meta:
        model = Foldings


class FoldingsInput(graphene.InputObjectType):
    processing_id = graphene.Int(name="processing_id", required=True)
    folding_ephemeris_id = graphene.Int(name="folding_ephemeris_id", required=True)
    nbin = graphene.Int(requried=True)
    npol = graphene.Int(requried=True)
    nchan = graphene.Int(requried=True)
    dm = graphene.Float(requried=True)
    tsubint = graphene.Float(requried=True)
