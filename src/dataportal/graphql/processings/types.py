from graphene_django import DjangoObjectType

from ...models import Processings


class ProcessingsType(DjangoObjectType):
    class Meta:
        model = Processings
