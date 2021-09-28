import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Projects
from .types import ProjectsInput, ProjectsType
from datetime import timedelta


class CreateProject(graphene.Mutation):
    class Arguments:
        input = ProjectsInput(required=True)

    project = graphene.Field(ProjectsType)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, input):
        project, _ = Projects.objects.get_or_create(
            program_id=input.program_id,
            code=input.code,
            short=input.short,
            embargo_period=timedelta(days=input.embargo_period),
            description=input.description,
        )
        return CreateProject(project=project)


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProjectsInput(required=True)

    project = graphene.Field(ProjectsType)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, id, input):
        try:
            project = Projects.objects.get(pk=id)
            project.program_id = input.program_id
            project.code = input.code
            project.short = input.short
            project.embargo_period = timedelta(days=input.embargo_period)
            project.description = input.description
            project.save()
            return UpdateProject(project=project)
        except:
            return UpdateProject(project=None)


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    project = graphene.Field(ProjectsType)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, id):
        Projects.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
