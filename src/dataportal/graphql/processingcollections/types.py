from graphene_django import DjangoObjectType

from ...models import Processingcollections


class ProcessingcollectionsType(DjangoObjectType):
    class Meta:
        model = Processingcollections
