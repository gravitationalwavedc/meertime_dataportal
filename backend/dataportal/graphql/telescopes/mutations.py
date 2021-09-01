import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Telescopes
from .types import TelescopesInput, TelescopesType


class CreateTelescope(graphene.Mutation):
    class Arguments:
        input = TelescopesInput(required=True)

    telescope = graphene.Field(TelescopesType)

    @classmethod
    @permission_required("dataportal.add_telescopes")
    def mutate(cls, self, info, input):
        telescope, _ = Telescopes.objects.get_or_create(**input.__dict__)
        return CreateTelescope(telescope=telescope)


class UpdateTelescope(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TelescopesInput(required=True)

    telescope = graphene.Field(TelescopesType)

    @classmethod
    @permission_required("dataportal.add_telescopes")
    def mutate(cls, self, info, id, input):
        try:
            telescope = Telescopes.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(telescope, key, val)
            telescope.save()
            return UpdateTelescope(telescope=telescope)
        except:
            return UpdateTelescope(telescope=None)


class DeleteTelescope(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_telescopes")
    def mutate(cls, self, info, id):
        Telescopes.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_telescope = CreateTelescope.Field()
    update_telescope = UpdateTelescope.Field()
    delete_telescope = DeleteTelescope.Field()
