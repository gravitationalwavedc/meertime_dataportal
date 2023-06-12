import json
import pytz
from datetime import timedelta

import graphene
from graphql_jwt.decorators import permission_required
from graphene_django import DjangoObjectType

from utils.ephemeris import parse_ephemeris_file
from dataportal.models import (
    Observation,
    Pulsar,
    Telescope,
    Project,
    Session,
    Calibration,
    Ephemeris,
)


class ObservationType(DjangoObjectType):
    class Meta:
        model = Observation


class ObservationInput(graphene.InputObjectType):
    pulsarName = graphene.String(required=True)
    telescopeName = graphene.String(required=True)
    projectCode = graphene.String(required=True)
    calibrationId = graphene.Int(required=True)

    frequency = graphene.Float()
    bandwidth = graphene.Float()
    nchan = graphene.Int()

    # Antenna
    beam = graphene.Int()
    nant = graphene.Int()
    nantEff = graphene.Int()
    npol = graphene.Int()

    obsType = graphene.String()
    utcStart = graphene.DateTime()
    raj = graphene.String()
    decj = graphene.String()
    duration = graphene.Float()
    nbit = graphene.Int()
    tsamp = graphene.Float()

    # Backend folding values
    ephemerisText = graphene.String()
    foldNbin = graphene.Int()
    foldNchan = graphene.Int()
    foldTsubint = graphene.Int()

    # Backend search values
    filterbankNbit = graphene.Int()
    filterbankNpol = graphene.Int()
    filterbankNchan = graphene.Int()
    filterbankTsamp = graphene.Float()
    filterbankDm = graphene.Float()


class CreateObservation(graphene.Mutation):
    class Arguments:
        input = ObservationInput()

    observation = graphene.Field(ObservationType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, input=None):
        # Get foreign key models
        pulsar = Pulsar.objects.get(name=input["pulsarName"])
        telescope = Telescope.objects.get(name=input["telescopeName"])
        project = Project.objects.get(code=input["projectCode"])
        calibration = Calibration.objects.get(id=input["calibrationId"])

        # Create a new session if it is the first one within two hours with this calibration
        utc_start = input["utcStart"].astimezone(pytz.utc)
        utc_end = utc_start + timedelta(0, input["duration"])
        two_hours_before = utc_start - timedelta(0, 7200)
        two_hours_after  = utc_end   + timedelta(0, 7200)
        try:
            session = Session.objects.get(
                calibration=calibration,
                start__gte=two_hours_before,
                end__lte=two_hours_after,
            )
            # Session exists so update start or end time
            if utc_start < session.start:
                session.start = utc_start
            if utc_end > session.end:
                session.end   = utc_end
        except Session.DoesNotExist:
            # No session exists so make one
            session = Session.objects.create(
                calibration=calibration,
                start=utc_start,
                end=utc_end,
            )

        # Fold mode specific values
        if input["obsType"] == "fold":
            # Get Ephemeris from the ephemeris file
            ephemeris_dict = parse_ephemeris_file(input["ephemerisText"])
            ephemeris, _ = Ephemeris.objects.get_or_create(
                pulsar=pulsar,
                project=project,
                # TODO add created_by
                ephemeris_data=json.dumps(ephemeris_dict),
                p0=ephemeris_dict["P0"],
                dm=ephemeris_dict["DM"],
                valid_from=ephemeris_dict["START"],
                valid_to=ephemeris_dict["FINISH"],
            )
            fold_nbin     = input["foldNbin"]
            fold_nchan    = input["foldNchan"]
            fold_tsubint  = input["foldTsubint"]
        else:
            ephemeris = None
            fold_nbin  = None
            fold_nchan = None
            fold_tsubint  = None

        # Backend search values
        if input["obsType"] == "search":
            filterbank_nbit  = input["filterbankNbit"]
            filterbank_npol  = input["filterbankNpol"]
            filterbank_nchan = input["filterbankNchan"]
            filterbank_tsamp = input["filterbankTsamp"]
            filterbank_dm    = input["filterbankDm"]
        else:
            filterbank_nbit  = None
            filterbank_npol  = None
            filterbank_nchan = None
            filterbank_tsamp = None
            filterbank_dm    = None

        # Use get_or_create to create the observations with the required fields and everything else put as defaults
        observation, _ = Observation.objects.get_or_create(
            pulsar=pulsar,
            telescope=telescope,
            project=project,
            session=session,
            utc_start=input["utcStart"],
            beam=input["beam"],
            defaults={
                "frequency": input["frequency"],
                "bandwidth": input["bandwidth"],
                "nchan": input["nchan"],
                "nant": input["nant"],
                "nant_eff": input["nantEff"],
                "npol": input["npol"],
                "obs_type": input["obsType"],
                "raj": input["raj"],
                "decj": input["decj"],
                "duration": input["duration"],
                "nbit": input["nbit"],
                "tsamp": input["tsamp"],
                "ephemeris": ephemeris,
                "fold_nbin": fold_nbin,
                "fold_nchan": fold_nchan,
                "fold_tsubint": fold_tsubint,
                "filterbank_nbit": filterbank_nbit,
                "filterbank_npol": filterbank_npol,
                "filterbank_nchan": filterbank_nchan,
                "filterbank_tsamp": filterbank_tsamp,
                "filterbank_dm": filterbank_dm,
            }
        )
        return CreateObservation(observation=observation)


class UpdateObservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ObservationInput(required=True)

    observation = graphene.Field(ObservationType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, id, input=None):
        try:
            observation = Observation.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(observation, key, val)
            observation.save()
            return UpdateObservation(observation=observation)
        except:
            return UpdateObservation(observation=None)


class DeleteObservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, id):
        Observation.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    createObservation = CreateObservation.Field()
    updateObservation = UpdateObservation.Field()
    deleteObservation = DeleteObservation.Field()