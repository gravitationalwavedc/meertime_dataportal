from graphene_django import DjangoObjectType
import graphene

from dataportal.models import Collections


class CollectionsType(DjangoObjectType):
    class Meta:
        model = Collections


class CollectionsInput(graphene.InputObjectType):
    name = graphene.String(name="name", required=True)
    description = graphene.String(name="description", required=True)
