import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required

from dataportal.models import Telescope
from datetime import timedelta


class TelescopeType(DjangoObjectType):
    class Meta:
        model = Telescope


class TelescopeInput(graphene.InputObjectType):
    name = graphene.String(required=True)


class CreateTelescope(graphene.Mutation):
    class Arguments:
        input = TelescopeInput(required=True)

    telescope = graphene.Field(TelescopeType)

    @classmethod
    @permission_required("dataportal.add_telescope")
    def mutate(cls, self, info, input):
        telescope, _ = Telescope.objects.get_or_create(**input.__dict__)
        return CreateTelescope(telescope=telescope)


class UpdateTelescope(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TelescopeInput(required=True)

    telescope = graphene.Field(TelescopeType)

    @classmethod
    @permission_required("dataportal.add_telescope")
    def mutate(cls, self, info, id, input):
        try:
            telescope = Telescope.objects.get(pk=id)
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
    @permission_required("dataportal.add_telescope")
    def mutate(cls, self, info, id):
        Telescope.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_telescope = CreateTelescope.Field()
    update_telescope = UpdateTelescope.Field()
    delete_telescope = DeleteTelescope.Field()
