import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateTelescope(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    telescope = graphene.Field(TelescopesType)

    @classmethod
    @permission_required("dataportal.add_telescopes")
    def mutate(cls, self, info, name):
        _telescope, _ = Telescopes.objects.get_or_create(name=name)
        return CreateTelescope(telescope=_telescope)


class Mutation(graphene.ObjectType):
    create_telescope = CreateTelescope.Field()
