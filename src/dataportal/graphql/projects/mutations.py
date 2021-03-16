import graphene
from graphql_jwt.decorators import permission_required
from .types import *
from datetime import timedelta


class CreateProject(graphene.Mutation):
    class Arguments:
        code = graphene.String()
        short = graphene.String()
        embargo_period = graphene.Int()
        description = graphene.String()

    project = graphene.Field(ProjectsType)

    @classmethod
    @permission_required("dataportal.add_projects")
    def mutate(cls, self, info, code, short, embargo_period, description):
        _project, _ = Projects.objects.get_or_create(
            code=code, short=short, embargo_period=timedelta(days=embargo_period), description=description
        )
        return CreateProject(project=_project)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
