import graphene
from graphql_jwt.decorators import login_required
from .types import *
from ...models import Templates


class Query(graphene.ObjectType):
    templates = graphene.List(TemplatesType)

    @login_required
    def resolve_templates(cls, info, **kwargs):
        return Templates.objects.all()
