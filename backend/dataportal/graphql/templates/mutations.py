import graphene
from graphql_jwt.decorators import permission_required
from decimal import Decimal
from dataportal.models import Templates
from .types import TemplatesInput, TemplatesType


class CreateTemplate(graphene.Mutation):
    class Arguments:
        input = TemplatesInput(required=True)

    template = graphene.Field(TemplatesType)

    @classmethod
    @permission_required("dataportal.add_templates")
    def mutate(cls, self, info, input):
        template, _ = Templates.objects.get_or_create(**input.__dict__)
        return CreateTemplate(template=template)


class UpdateTemplate(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TemplatesInput(required=True)

    template = graphene.Field(TemplatesType)

    @classmethod
    @permission_required("dataportal.add_templates")
    def mutate(cls, self, info, id, input):
        try:
            template = Templates.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(template, key, val)
            template.save()
            return UpdateTemplate(template=template)
        except:
            return UpdateTemplate(template=None)


class DeleteTemplate(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_templates")
    def mutate(cls, self, info, id):
        Templates.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_template = CreateTemplate.Field()
    update_template = UpdateTemplate.Field()
    delete_template = DeleteTemplate.Field()
