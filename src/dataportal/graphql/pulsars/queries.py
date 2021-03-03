import graphene
from graphql_jwt.decorators import login_required
from .types import *


class Query(graphene.ObjectType):
    pulsars = graphene.List(PulsarsType)
    pulsarById = graphene.Field(PulsarsType, id=graphene.Int())
    pulsarsByJname = graphene.List(PulsarsType, jname=graphene.String())

    @login_required
    def resolve_pulsars(cls, info, **kwargs):
        return Pulsars.objects.all()

    @login_required
    def resolve_pulsarById(cls, info, **kwargs):
        id = kwargs.get("id")
        if id is not None:
            return Pulsars.objects.get(pk=id)
        return None

    @login_required
    def resolve_pulsarsByJname(cls, info, **kwargs):
        jname = kwargs.get("jname")
        if jname is not None:
            return Pulsars.objects.filter(jname=jname)
        return None
