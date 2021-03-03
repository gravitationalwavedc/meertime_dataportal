from graphene_django import DjangoObjectType

from ...models import Pulsars


class PulsarsType(DjangoObjectType):
    class Meta:
        model = Pulsars
