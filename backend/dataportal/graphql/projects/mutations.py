import graphene
from graphql_jwt.decorators import permission_required
from .types import *
from datetime import timedelta


class CreateProject(graphene.Mutation):
    class Arguments:
        input = ProjectsInput(required=True)

    project = graphene.Field(ProjectsType)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, input):
        _project, _ = Projects.objects.get_or_create(
            code=input.code,
            short=input.short,
            embargo_period=timedelta(days=input.embargo_period),
            description=input.description,
        )
        return CreateProject(project=_project)


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProjectsInput(required=True)

    project = graphene.Field(ProjectsType)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, id, input):
        _project = Projects.objects.get(pk=id)
        if _project:
            _project.code = input.code
            _project.short = input.short
            _project.embargo_period = timedelta(days=input.embargo_period)
            _project.description = input.description
            _project.save()
            return UpdateProject(project=_project)
        return UpdateProject(project=None)


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    project = graphene.Field(ProjectsType)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, id):
        _project = Projects.objects.get(pk=id)
        _project.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
