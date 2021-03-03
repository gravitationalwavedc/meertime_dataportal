from graphene_django import DjangoObjectType

from ...models import Ephemerides


class EphemeridesType(DjangoObjectType):
    class Meta:
        model = Ephemerides
