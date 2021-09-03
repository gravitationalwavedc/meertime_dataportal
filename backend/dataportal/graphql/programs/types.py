from graphene_django import DjangoObjectType
import graphene

from dataportal.models import Programs


class ProgramsType(DjangoObjectType):
    class Meta:
        model = Programs


class ProgramsInput(graphene.InputObjectType):
    telescope_id = graphene.Int(name="telescope_id", required=True)
    name = graphene.String(required=True)
