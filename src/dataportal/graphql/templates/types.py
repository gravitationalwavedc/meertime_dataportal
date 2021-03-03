from graphene_django import DjangoObjectType

from ...models import Templates


class TemplatesType(DjangoObjectType):
    class Meta:
        model = Templates
