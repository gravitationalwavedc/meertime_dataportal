from graphene_django import DjangoObjectType

from ...models import Launches


class LaunchesType(DjangoObjectType):
    class Meta:
        model = Launches
