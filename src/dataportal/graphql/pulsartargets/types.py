from graphene_django import DjangoObjectType

from ...models import Pulsartargets


class PulsartargetsType(DjangoObjectType):
    class Meta:
        model = Pulsartargets
