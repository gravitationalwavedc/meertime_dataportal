import json
import graphene
from graphql_jwt.decorators import permission_required
from django_mysql.models import JSONField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from utils.template import parse_template_file
from dataportal.models import (
    Template,
    Pulsar,
    Project,
)

@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class TemplateType(DjangoObjectType):
    class Meta:
        model = Template


class TemplateInput(graphene.InputObjectType):
    pulsar_name   = graphene.String(required=True)
    project_code  = graphene.String(required=True)
    template_loc = graphene.String(required=True)
    comment = graphene.String()


class CreateTemplate(graphene.Mutation):
    class Arguments:
        input = TemplateInput(required=True)

    template = graphene.Field(TemplateType)

    @classmethod
    @permission_required("dataportal.add_template")
    def mutate(cls, self, info, input):
        # Get foreign key models
        pulsar  = Pulsar.objects.get(name=input["pulsar_name"])
        project = Project.objects.get(code=input["project_code"])
        # Load the template file
        template_dict = parse_template_file(input["template_loc"])
        template = Template.objects.get_or_create(
            pulsar=pulsar,
            project=project,
            # TODO add created_by
            template_data=json.dumps(template_dict),
            p0=template_dict["P0"],
            dm=template_dict["DM"],
            valid_from=template_dict["START"],
            valid_to=template_dict["FINISH"],
            comment=input["comment"],
        )
        return CreateTemplate(template=template)


class UpdateTemplate(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TemplateInput(required=True)

    template = graphene.Field(TemplateType)

    @classmethod
    @permission_required("dataportal.add_ephemerides")
    def mutate(cls, self, info, id, input):
        _template = Template.objects.get(pk=id)
        if _template:
            for key, val in input.__dict__.items():
                limits = TemplateInput.limits.get(key)
                if limits:
                    deci_str = "1.".ljust(limits["deci"] + 2, "0")
                    val = val.quantize(Decimal(deci_str))
                setattr(_template, key, val)
            _template.save()
            return UpdateTemplate(template=_template)
        return UpdateTemplate(template=None)


class DeleteTemplate(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    template = graphene.Field(TemplateType)

    @classmethod
    @permission_required("dataportal.add_ephemerides")
    def mutate(cls, self, info, id):
        _template = Template.objects.get(pk=id)
        _template.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    createTemplate = CreateTemplate.Field()
    updateTemplate = UpdateTemplate.Field()
    deleteTemplate = DeleteTemplate.Field()
