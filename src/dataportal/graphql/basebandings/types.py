from graphene_django import DjangoObjectType

from ...models import Basebandings


class BasebandingsType(DjangoObjectType):
    class Meta:
        model = Basebandings
