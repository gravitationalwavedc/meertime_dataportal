from graphene_django import DjangoObjectType

from ...models import Rfis


class RfisType(DjangoObjectType):
    class Meta:
        model = Rfis
