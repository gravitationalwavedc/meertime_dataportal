from graphene_django import DjangoObjectType

from ...models import Projects


class ProjectsType(DjangoObjectType):
    class Meta:
        model = Projects
