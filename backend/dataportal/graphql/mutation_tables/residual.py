import json
from datetime import datetime, timedelta
from decimal import Decimal, getcontext

import graphene
from graphql_jwt.decorators import permission_required
from django.db import IntegrityError

from dataportal.models import Pulsar, Ephemeris, Project, Residual, Toa
from dataportal.graphql.queries import ResidualNode
from utils.ephemeris import parse_ephemeris_file



class ResidualInput(graphene.InputObjectType):
    # foreign keys
    pulsar       = graphene.String(required=True)
    projectShort = graphene.String(required=True)
    ephemerisText  = graphene.String(required=True)

    residualLines = graphene.List(graphene.String, required=True)


class CreateResidualOutput(graphene.ObjectType):
    residual = graphene.List(ResidualNode)


class CreateResidual(graphene.Mutation):
    class Arguments:
        input = ResidualInput(required=True)

    residual = graphene.List(ResidualNode)
    Output = CreateResidualOutput

    @classmethod
    @permission_required("dataportal.add_residual")
    def mutate(cls, self, info, input):
        # Get foreign keys
        pulsar    = Pulsar.objects.get(name=input["pulsar"])
        project   = Project.objects.get(short=input["projectShort"])

        # Load the ephemeris file and create get or create the ephemeris
        ephemeris_dict = parse_ephemeris_file(input["ephemerisText"])
        try:
            ephemeris, created = Ephemeris.objects.get_or_create(
                pulsar=pulsar,
                project=project,
                # TODO add created_by
                ephemeris_data=json.dumps(ephemeris_dict),
                p0=ephemeris_dict["P0"],
                dm=ephemeris_dict["DM"],
                valid_from=ephemeris_dict["START"],
                valid_to=ephemeris_dict["FINISH"],
            )
        except IntegrityError:
            # Handle the IntegrityError gracefully by grabbing the already created ephem
            ephemeris = Ephemeris.objects.get(
                pulsar=pulsar,
                project=project,
                ephemeris_data=json.dumps(ephemeris_dict),
            )

        # MJDs are stored as Decimals as standard floats don't have enough precision
        getcontext().prec = 12
        base_date = datetime(1858, 11, 17)  # Base date for MJD

        residual_to_create = []
        residual_lines = input["residualLines"]
        for residual_line in residual_lines:
            # Loop over residual lines and and split them to get the important values
            id, mjd, residual, residual_err, residual_phase = residual_line.split(",")
            # Get toa foreign key
            toa = Toa.objects.get(id=int(id))



            date = base_date + timedelta(days=float(mjd))
            # Get the day of the year as a float
            day_of_year = date.timetuple().tm_yday \
                + date.hour / 24.0 \
                + date.minute / (24.0 * 60.0) \
                + date.second / (24.0 * 60.0 * 60.0)

            # Upload the residual
            residual_to_create.append(
                Residual(
                    toa=toa,
                    pulsar=pulsar,
                    project=project,
                    ephemeris=ephemeris,
                    # X axis types
                    mjd               =Decimal(mjd),
                    day_of_year       =day_of_year,
                    # binary_orbital_phase=residual_dict["binary_orbital_phase"],
                    # Y axis types
                    residual_sec      =float(residual),
                    residual_sec_err  =float(residual_err)/1e9, # Convert from ns to s
                    residual_phase    =float(residual_phase),
                    # Convert from ns to s the divide vy period to convert to phase
                    residual_phase_err=float(residual_err)/1e9 / ephemeris_dict["P0"],
                )
            )
        created_residuals = Residual.objects.bulk_create(residual_to_create)
        return CreateResidualOutput(residual=created_residuals)


class UpdateResidual(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ResidualInput(required=True)

    residual = graphene.Field(ResidualNode)

    @classmethod
    @permission_required("dataportal.add_residual")
    def mutate(cls, self, info, id, input):
        try:
            residual = Residual.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(residual, key, val)
            residual.save()
            return UpdateResidual(residual=residual)
        except:
            return UpdateResidual(residual=None)


class DeleteResidual(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_residual")
    def mutate(cls, self, info, id):
        Residual.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_residual = CreateResidual.Field()
    update_residual = UpdateResidual.Field()
    delete_residual = DeleteResidual.Field()
