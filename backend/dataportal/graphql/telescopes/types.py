import graphene
from graphene_django import DjangoObjectType

from dataportal.models import Telescopes


class TelescopesType(DjangoObjectType):
    class Meta:
        model = Telescopes


class TelescopesInput(graphene.InputObjectType):
    name = graphene.String(required=True)
