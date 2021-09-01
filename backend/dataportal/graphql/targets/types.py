from graphene_django import DjangoObjectType
import graphene

from dataportal.models import Targets


class TargetsType(DjangoObjectType):
    class Meta:
        model = Targets


class TargetsInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    raj = graphene.String(required=True)
    decj = graphene.String(required=True)
