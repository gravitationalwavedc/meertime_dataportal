import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateTelescope(graphene.Mutation):
    class Arguments:
        input = TelescopesInput(required=True)

    telescope = graphene.Field(TelescopesType)

    @classmethod
    @permission_required("dataportal.add_telescopes")
    def mutate(cls, self, info, input):
        _telescope, _ = Telescopes.objects.get_or_create(**input.__dict__)
        return CreateTelescope(telescope=_telescope)


class UpdateTelescope(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TelescopesInput(required=True)

    telescope = graphene.Field(TelescopesType)

    @classmethod
    @permission_required("dataportal.add_telescopes")
    def mutate(cls, self, info, id, input):
        _telescope = Telescopes.objects.get(pk=id)
        if _telescope:
            for key, val in input.__dict__.items():
                setattr(_telescope, key, val)
            _telescope.save()
            return UpdateTelescope(telescope=_telescope)
        return UpdateTelescope(telescope=None)


class DeleteTelescope(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    telescope = graphene.Field(TelescopesType)

    @classmethod
    @permission_required("dataportal.add_telescopes")
    def mutate(cls, self, info, id):
        _telescope = Telescopes.objects.get(pk=id)
        _telescope.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_telescope = CreateTelescope.Field()
    update_telescope = UpdateTelescope.Field()
    delete_telescope = DeleteTelescope.Field()
