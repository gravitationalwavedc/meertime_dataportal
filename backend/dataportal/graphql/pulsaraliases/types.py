from graphene_django import DjangoObjectType

from ...models import Pulsaraliases


class PulsaraliasesType(DjangoObjectType):
    class Meta:
        model = Pulsaraliases
