import graphene
from graphql_jwt.decorators import permission_required

from . import pulsars, pipelines, targets


class Mutation(pulsars.Mutation, pipelines.Mutation, targets.Mutation, graphene.ObjectType):
    pass
