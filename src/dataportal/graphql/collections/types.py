from graphene_django import DjangoObjectType

from ...models import Collections


class CollectionsType(DjangoObjectType):
    class Meta:
        model = Collections
