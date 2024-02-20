import json
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal, getcontext

import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Pulsar, Ephemeris, Project, Toa
from dataportal.graphql.queries import ToaNode
from utils.binary_phase import get_binary_phase, is_binary



class ResidualInput(graphene.InputObjectType):
    residualLines = graphene.List(graphene.String, required=True)


class CreateResidualOutput(graphene.ObjectType):
    toa = graphene.List(ToaNode)


class CreateResidual(graphene.Mutation):
    class Arguments:
        input = ResidualInput(required=True)

    Output = CreateResidualOutput

    @classmethod
    @permission_required("dataportal.add_residual")
    def mutate(cls, self, info, input):


        # MJDs are stored as Decimals as standard floats don't have enough precision
        getcontext().prec = 12
        base_date = datetime(1858, 11, 17)  # Base date for MJD

        toas_to_update = []
        residual_info = {}
        for residual_line in input["residualLines"]:
            # Loop over residual lines and and split them to get the important values
            id, mjd, residual, residual_err, residual_phase = residual_line.split(",")
            # Put thin info into a dict to be used later
            residual_info[int(id)] = {
                "mjd":            mjd,
                "residual":       residual,
                "residual_err":   residual_err,
                "residual_phase": residual_phase,
            }

        # Use a filter instead of thousands of individual gets for speed
        toas_to_update = Toa.objects.select_related("ephemeris").filter(id__in=residual_info.keys())
        for toa in toas_to_update:
            # Unpack
            mjd = residual_info[toa.id]["mjd"]
            residual = residual_info[toa.id]["residual"]
            residual_err = residual_info[toa.id]["residual_err"]
            residual_phase = residual_info[toa.id]["residual_phase"]

            ephemeris_dict = json.loads(toa.ephemeris.ephemeris_data)

            # Get the day of the year as a float
            date = base_date + timedelta(days=float(mjd))
            day_of_year = date.timetuple().tm_yday \
                + date.hour / 24.0 \
                + date.minute / (1440.0) \
                + date.second / (86400.0)
                # 24.0 * 60.0 = 1440.0
                # 24.0 * 60.0 * 60.0 = 86400.0

            if is_binary(ephemeris_dict):
                # If the pulsar is a binary then we need to calculate the phase
                binary_orbital_phase = get_binary_phase(np.array([float(mjd)]), ephemeris_dict)[0]
            else:
                binary_orbital_phase = None

            # Update the toa with the residual
            # X axis types
            toa.day_of_year = day_of_year
            toa.binary_orbital_phase = binary_orbital_phase
            # Y axis types
            toa.residual_sec = float(residual)
            toa.residual_sec_err = float(residual_err)/1e9 # Convert from ns to s
            toa.residual_phase = float(residual_phase)
            # Convert from ns to s the divide by period to convert to phase
            toa.residual_phase_err = float(residual_err)/1e9 / ephemeris_dict["P0"]


        # Launch bulk creation of residuals (update of toas)
        n_toas_updated = Toa.objects.bulk_update(
            toas_to_update,
            [
                "day_of_year",
                "binary_orbital_phase",
                "residual_sec",
                "residual_sec_err",
                "residual_phase",
                "residual_phase_err",
            ]
        )

        return CreateResidualOutput(toa=toas_to_update)


class Mutation(graphene.ObjectType):
    create_residual = CreateResidual.Field()
