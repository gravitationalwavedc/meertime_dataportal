from graphene_django import DjangoObjectType
import graphene

from dataportal.models import Sessions


class SessionsType(DjangoObjectType):
    class Meta:
        model = Sessions


class SessionsInput(graphene.InputObjectType):
    telescope_id = graphene.Int(name="telescope_id", required=True)
    start = graphene.DateTime(required=True)
    end = graphene.DateTime(required=True)
