import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Projects


class Query(graphene.ObjectType):
    projects = graphene.List(ProjectsType)

    @login_required
    def resolve_projects(cls, info, **kwargs):
        return Projects.objects.all()
