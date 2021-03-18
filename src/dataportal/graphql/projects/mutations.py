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


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
