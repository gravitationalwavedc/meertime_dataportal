from graphene_django import DjangoObjectType

from ...models import Observations


class ObservationsType(DjangoObjectType):
    class Meta:
        model = Observations
