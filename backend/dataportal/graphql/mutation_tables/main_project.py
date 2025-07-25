import graphene
from django.db.models.fields import DurationField
from graphene_django.converter import convert_django_field

from dataportal.graphql.queries import MainProjectNode
from dataportal.models import MainProject, Telescope
from user_manage.graphql.decorators import permission_required


@convert_django_field.register(DurationField)
def convert_duration_field_to_string(field, registry=None):
    return graphene.String()


class MainProjectInput(graphene.InputObjectType):
    telescope_name = graphene.String(required="True")
    name = graphene.String(required="True")


class CreateMainProject(graphene.Mutation):
    class Arguments:
        input = MainProjectInput(required=True)

    mainproject = graphene.Field(MainProjectNode)

    @permission_required("dataportal.add_main_project")
    def mutate(root, info, input):
        telescope = Telescope.objects.get(name=input["telescope_name"])
        main_project, _ = MainProject.objects.get_or_create(
            telescope=telescope,
            name=input.name,
        )
        return CreateMainProject(mainproject=main_project)


class UpdateMainProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = MainProjectInput(required=True)

    mainproject = graphene.Field(MainProjectNode)

    @permission_required("dataportal.add_main_project")
    def mutate(root, info, id, input):
        try:
            telescope = Telescope.objects.get(name=input["telescope_name"])
            main_project = MainProject.objects.get(pk=id)
            main_project.telescope = telescope
            main_project.name = input.name
            main_project.save()
            return UpdateMainProject(mainproject=main_project)
        except Exception:
            return UpdateMainProject(mainproject=None)


class DeleteMainProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    mainproject = graphene.Field(MainProjectNode)

    @permission_required("dataportal.add_main_project")
    def mutate(root, info, id):
        MainProject.objects.get(pk=id).delete()
        return DeleteMainProject(ok=True)


class Mutation(graphene.ObjectType):
    createMainProject = CreateMainProject.Field()
    updateMainProject = UpdateMainProject.Field()
    deleteMainProject = DeleteMainProject.Field()
