import graphene

from dataportal.graphql.queries import TelescopeNode
from dataportal.models import Telescope
from user_manage.graphql.decorators import permission_required


class TelescopeInput(graphene.InputObjectType):
    name = graphene.String(required=True)


class CreateTelescope(graphene.Mutation):
    class Arguments:
        input = TelescopeInput(required=True)

    telescope = graphene.Field(TelescopeNode)

    @permission_required("dataportal.add_telescope")
    def mutate(root, info, input):
        telescope, _ = Telescope.objects.get_or_create(**input.__dict__)
        return CreateTelescope(telescope=telescope)


class UpdateTelescope(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TelescopeInput(required=True)

    telescope = graphene.Field(TelescopeNode)

    @permission_required("dataportal.add_telescope")
    def mutate(root, info, id, input):
        try:
            telescope = Telescope.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(telescope, key, val)
            telescope.save()
            return UpdateTelescope(telescope=telescope)
        except Exception:
            return UpdateTelescope(telescope=None)


class DeleteTelescope(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @permission_required("dataportal.add_telescope")
    def mutate(root, info, id):
        Telescope.objects.get(pk=id).delete()
        return DeleteTelescope(ok=True)


class Mutation(graphene.ObjectType):
    create_telescope = CreateTelescope.Field()
    update_telescope = UpdateTelescope.Field()
    delete_telescope = DeleteTelescope.Field()
