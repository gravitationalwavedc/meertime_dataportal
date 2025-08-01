import json
from decimal import Decimal

import graphene
from django.contrib.postgres.fields import JSONField
from django.db import IntegrityError
from graphene_django.converter import convert_django_field

from dataportal.graphql.queries import EphemerisNode
from dataportal.models import Ephemeris, Project, Pulsar
from user_manage.graphql.decorators import permission_required
from utils.ephemeris import parse_ephemeris_file


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.JSONString()


class EphemerisInput(graphene.InputObjectType):
    pulsarName = graphene.String(required=True)
    ephemerisText = graphene.String(required=True)
    projectCode = graphene.String()
    projectShort = graphene.String()
    comment = graphene.String()


class CreateEphemeris(graphene.Mutation):
    class Arguments:
        input = EphemerisInput()

    ephemeris = graphene.Field(EphemerisNode)

    @permission_required("dataportal.add_ephemeris")
    def mutate(root, info, input):
        # Get foreign key models
        pulsar = Pulsar.objects.get(name=input["pulsarName"])
        if input["projectCode"] is not None:
            project = Project.objects.get(code=input["projectCode"])
        elif input["projectShort"] is not None:
            project = Project.objects.get(short=input["projectShort"])
        else:
            # Should have a project code or short so I can't create an ephemeris
            project = None

        # Load the ephemeris file
        ephemeris_dict = parse_ephemeris_file(input["ephemerisText"])
        try:
            ephemeris, _ = Ephemeris.objects.get_or_create(
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
        except IntegrityError:
            # Handle the IntegrityError gracefully by grabbing the already created ephem
            ephemeris = Ephemeris.objects.get(
                pulsar=pulsar,
                project=project,
                ephemeris_data=json.dumps(ephemeris_dict),
            )
            return CreateEphemeris(ephemeris=ephemeris)


class UpdateEphemeris(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = EphemerisInput(required=True)

    ephemeris = graphene.Field(EphemerisNode)

    @permission_required("dataportal.add_ephemerides")
    def mutate(root, info, id, input):
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
    ephemeris = graphene.Field(EphemerisNode)

    @permission_required("dataportal.add_ephemerides")
    def mutate(root, info, id):
        _ephemeris = Ephemeris.objects.get(pk=id)
        _ephemeris.delete()
        return DeleteEphemeris(ok=True)


class Mutation(graphene.ObjectType):
    create_ephemeris = CreateEphemeris.Field()
    update_ephemeris = UpdateEphemeris.Field()
    delete_ephemeris = DeleteEphemeris.Field()
