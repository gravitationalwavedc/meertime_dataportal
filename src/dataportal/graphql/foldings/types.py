from graphene_django import DjangoObjectType

from ...models import Foldings


class FoldingsType(DjangoObjectType):
    class Meta:
        model = Foldings
