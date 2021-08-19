from graphene_django import DjangoObjectType

from ...models import Toas


class ToasType(DjangoObjectType):
    class Meta:
        model = Toas
