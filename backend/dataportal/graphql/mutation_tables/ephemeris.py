import json
import graphene
from graphql_jwt.decorators import permission_required
from django_mysql.models import JSONField
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from utils.ephemeris import parse_ephemeris_file
from dataportal.models import Ephemeris
from dataportal.models import (
    Ephemeris,
    Pulsar,
    Project,
)

@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class EphemerisType(DjangoObjectType):
    class Meta:
        model = Ephemeris


class EphemerisInput(graphene.InputObjectType):
    pulsar_name   = graphene.String(required=True)
    project_code  = graphene.String(required=True)
    ephemeris_loc = graphene.String(required=True)
    comment = graphene.String(required=True)


class CreateEphemeris(graphene.Mutation):
    class Arguments:
        input = EphemerisInput(required=True)

    ephemeris = graphene.Field(EphemerisType)

    @classmethod
    @permission_required("dataportal.add_ephemeris")
    def mutate(cls, self, info, input):
        # Get foreign key models
        pulsar  = Pulsar.objects.get(name=input["pulsar_name"])
        project = Project.objects.get(code=input["project_code"])
        # Load the ephemeris file
        ephemeris_dict = parse_ephemeris_file(input["ephemeris_loc"])
        ephemeris = Ephemeris.objects.get_or_create(
            pulsar=pulsar,
            project=project,
            # TODO add created_by
            ephemeris_data=json.dumps(ephemeris_dict),
            p0=ephemeris_dict["P0"],
            dm=ephemeris_dict["DM"],
            valid_from=ephemeris_dict["START"],
            valid_to=ephemeris_dict["FINISH"],
            comment=input["comment"],
        )
        return CreateEphemeris(ephemeris=ephemeris)


class UpdateEphemeris(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = EphemerisInput(required=True)

    ephemeris = graphene.Field(EphemerisType)

    @classmethod
    @permission_required("dataportal.add_ephemerides")
    def mutate(cls, self, info, id, input):
        _ephemeris = Ephemeris.objects.get(pk=id)
        if _ephemeris:
            for key, val in input.__dict__.items():
                limits = EphemerisInput.limits.get(key)
                if limits:
                    deci_str = "1.".ljust(limits["deci"] + 2, "0")
                    val = val.quantize(Decimal(deci_str))
                setattr(_ephemeris, key, val)
            _ephemeris.save()
            return UpdateEphemeris(ephemeris=_ephemeris)
        return UpdateEphemeris(ephemeris=None)


class DeleteEphemeris(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    ephemeris = graphene.Field(EphemerisType)

    @classmethod
    @permission_required("dataportal.add_ephemerides")
    def mutate(cls, self, info, id):
        _ephemeris = Ephemeris.objects.get(pk=id)
        _ephemeris.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_ephemeris = CreateEphemeris.Field()
    update_ephemeris = UpdateEphemeris.Field()
    delete_ephemeris = DeleteEphemeris.Field()
