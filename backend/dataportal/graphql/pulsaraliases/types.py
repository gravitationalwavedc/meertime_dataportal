from graphene_django import DjangoObjectType

from dataportal.models import Pulsaraliases


class PulsaraliasesType(DjangoObjectType):
    class Meta:
        model = Pulsaraliases
