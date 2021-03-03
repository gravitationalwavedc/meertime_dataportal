from graphene_django import DjangoObjectType

from ...models import Instrumentconfigs


class InstrumentconfigsType(DjangoObjectType):
    class Meta:
        model = Instrumentconfigs
