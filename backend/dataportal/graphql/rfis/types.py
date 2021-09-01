from graphene_django import DjangoObjectType

from dataportal.models import Rfis


class RfisType(DjangoObjectType):
    class Meta:
        model = Rfis
