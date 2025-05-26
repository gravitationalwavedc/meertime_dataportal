import json

import graphene
from django.db import IntegrityError
from user_manage.graphql.decorators import permission_required

from dataportal.graphql.queries import ObservationNode
from dataportal.models import Calibration, Ephemeris, Observation, Project, Pulsar, Telescope
from utils.ephemeris import parse_ephemeris_file


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

    observation = graphene.Field(ObservationNode)

    @permission_required("dataportal.add_observations")
    def mutate(root, info, input=None):
        # Get foreign key models
        pulsar = Pulsar.objects.get(name=input["pulsarName"])
        telescope = Telescope.objects.get(name=input["telescopeName"])
        project = Project.objects.get(code=input["projectCode"])
        calibration = Calibration.objects.get(id=input["calibrationId"])

        # Fold mode specific values
        if input["obsType"] == "fold":
            # Get Ephemeris from the ephemeris file
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
                )
            except IntegrityError:
                # Handle the IntegrityError gracefully by grabbing the already created ephem
                ephemeris = Ephemeris.objects.get(
                    project=project,
                    ephemeris_data=json.dumps(ephemeris_dict),
                )
            fold_nbin = input["foldNbin"]
            fold_nchan = input["foldNchan"]
            fold_tsubint = input["foldTsubint"]
        else:
            ephemeris = None
            fold_nbin = None
            fold_nchan = None
            fold_tsubint = None

        # Backend search values
        if input["obsType"] == "search":
            filterbank_nbit = input["filterbankNbit"]
            filterbank_npol = input["filterbankNpol"]
            filterbank_nchan = input["filterbankNchan"]
            filterbank_tsamp = input["filterbankTsamp"]
            filterbank_dm = input["filterbankDm"]
        else:
            filterbank_nbit = None
            filterbank_npol = None
            filterbank_nchan = None
            filterbank_tsamp = None
            filterbank_dm = None

        # Use get_or_create to create the observations with the required fields and everything else put as defaults
        observation, created = Observation.objects.get_or_create(
            pulsar=pulsar,
            telescope=telescope,
            project=project,
            utc_start=input["utcStart"],
            beam=input["beam"],
            defaults={
                "calibration": calibration,
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
            },
        )
        if not created:
            # If the observation already exists, update the values
            observation.calibration = calibration
            observation.frequency = input["frequency"]
            observation.bandwidth = input["bandwidth"]
            observation.nchan = input["nchan"]
            observation.nant = input["nant"]
            observation.nant_eff = input["nantEff"]
            observation.npol = input["npol"]
            observation.obs_type = input["obsType"]
            observation.raj = input["raj"]
            observation.decj = input["decj"]
            observation.duration = input["duration"]
            observation.nbit = input["nbit"]
            observation.tsamp = input["tsamp"]
            observation.ephemeris = ephemeris
            observation.fold_nbin = fold_nbin
            observation.fold_nchan = fold_nchan
            observation.fold_tsubint = fold_tsubint
            observation.filterbank_nbit = filterbank_nbit
            observation.filterbank_npol = filterbank_npol
            observation.filterbank_nchan = filterbank_nchan
            observation.filterbank_tsamp = filterbank_tsamp
            observation.filterbank_dm = filterbank_dm
            observation.save()
        return CreateObservation(observation=observation)


class UpdateObservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ObservationInput(required=True)

    observation = graphene.Field(ObservationNode)

    @permission_required("dataportal.add_observations")
    def mutate(root, info, id, input=None):
        try:
            observation = Observation.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(observation, key, val)
            observation.save()
            return UpdateObservation(observation=observation)
        except Exception:
            return UpdateObservation(observation=None)


class DeleteObservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @permission_required("dataportal.add_observations")
    def mutate(root, info, id):
        Observation.objects.get(pk=id).delete()
        return DeleteObservation(ok=True)


class Mutation(graphene.ObjectType):
    createObservation = CreateObservation.Field()
    updateObservation = UpdateObservation.Field()
    deleteObservation = DeleteObservation.Field()
