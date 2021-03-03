from graphene_django import DjangoObjectType
from ...models import Targets


class TargetsType(DjangoObjectType):
    class Meta:
        model = Targets
