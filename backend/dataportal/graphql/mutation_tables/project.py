from datetime import timedelta

import graphene
from django.db.models.fields import DurationField
from graphene_django.converter import convert_django_field
from graphql_jwt.decorators import permission_required

from dataportal.graphql.queries import ProjectNode
from dataportal.models import MainProject, Project


@convert_django_field.register(DurationField)
def convert_duration_field_to_string(field, registry=None):
    return graphene.String()


class ProjectInput(graphene.InputObjectType):
    main_project_name = graphene.String(required="True")
    code = graphene.String()
    short = graphene.String()
    embargo_period = graphene.Int()
    description = graphene.String()


class CreateProject(graphene.Mutation):
    class Arguments:
        input = ProjectInput(required=True)

    project = graphene.Field(ProjectNode)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, input):
        main_project = MainProject.objects.get(name=input["main_project_name"])
        project, _ = Project.objects.get_or_create(
            main_project=main_project,
            code=input.code,
            short=input.short,
            embargo_period=timedelta(days=input.embargo_period),
            description=input.description,
        )
        return CreateProject(project=project)


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProjectInput(required=True)

    project = graphene.Field(ProjectNode)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, id, input):
        try:
            main_project = MainProject.objects.get(name=input["main_project_name"])
            project = Project.objects.get(pk=id)
            project.main_project = main_project
            project.code = input.code
            project.short = input.short
            project.embargo_period = timedelta(days=input.embargo_period)
            project.description = input.description
            project.save()
            return UpdateProject(project=project)
        except Exception:
            return UpdateProject(project=None)


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    project = graphene.Field(ProjectNode)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, id):
        Project.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    createProject = CreateProject.Field()
    updateProject = UpdateProject.Field()
    deleteProject = DeleteProject.Field()
