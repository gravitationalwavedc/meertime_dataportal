from graphene_django import DjangoObjectType

from ...models import Filterbankings


class FilterbankingsType(DjangoObjectType):
    class Meta:
        model = Filterbankings
