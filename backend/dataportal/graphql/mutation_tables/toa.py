import json
import graphene
from graphql_jwt.decorators import permission_required
from graphql import GraphQLError
from django.db import IntegrityError

from dataportal.models import Toa, PipelineRun, Ephemeris, Template, Observation, Project
from dataportal.graphql.queries import ToaNode
from utils.toa import toa_line_to_dict, toa_dict_to_line
from utils.ephemeris import parse_ephemeris_file


class ToaInput(graphene.InputObjectType):
    # foreign keys
    pipelineRunId = graphene.Int(required=True)
    projectShort  = graphene.String(required=True)

    ephemerisText = graphene.String(required=True)
    templateId    = graphene.Int(required=True)

    toaLines = graphene.List(graphene.String, required=True)

    dmCorrected  = graphene.Boolean(required=True)
    minimumNsubs = graphene.Boolean(required=True)
    maximumNsubs = graphene.Boolean(required=True)


class CreateToaOutput(graphene.ObjectType):
    toa = graphene.List(ToaNode)


class CreateToa(graphene.Mutation):
    class Arguments:
        input = ToaInput(required=True)

    toa    = graphene.List(ToaNode)
    Output = CreateToaOutput

    @classmethod
    @permission_required("dataportal.add_toa")
    def mutate(cls, self, info, input):
        pipeline_run = PipelineRun.objects.get(id=input["pipelineRunId"])
        observation  = pipeline_run.observation
        project      = Project.objects.get(short=input["projectShort"])
        template     = Template.objects.get(id=input["templateId"])

        ephemeris_dict = parse_ephemeris_file(input["ephemerisText"])
        try:
            ephemeris, _ = Ephemeris.objects.get_or_create(
                pulsar=observation.pulsar,
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
                pulsar=observation.pulsar,
                project=project,
                ephemeris_data=json.dumps(ephemeris_dict),
            )

        # created_toas = []
        toas_to_create = []
        toa_lines = input["toaLines"]
        for toa_line in toa_lines[1:]:
            toa_line = toa_line.rstrip("\n")
            # Loop over toa lines and turn into a dict
            toa_dict = toa_line_to_dict(toa_line)
            # Revert it back to a line and check it matches before uploading
            output_toa_line = toa_dict_to_line(toa_dict)
            if toa_line != output_toa_line:
                raise GraphQLError(f"Assertion failed. toa_line and output_toa_line do not match.\n{toa_line}\n{output_toa_line}")
            # Upload the toa
            # toa = Toa.objects.create(
            toas_to_create.append(
                Toa(
                    pipeline_run=pipeline_run,
                    observation =observation,
                    project     =project,
                    ephemeris   =ephemeris,
                    template    =template,
                    archive     =toa_dict["archive"],
                    freq_MHz    =toa_dict["freq_MHz"],
                    mjd         =toa_dict["mjd"],
                    mjd_err     =toa_dict["mjd_err"],
                    telescope   =toa_dict["telescope"],
                    fe          =toa_dict["fe"],
                    be          =toa_dict["be"],
                    f           =toa_dict["f"],
                    bw          =toa_dict["bw"],
                    tobs        =toa_dict["tobs"],
                    tmplt       =toa_dict["tmplt"],
                    gof         =toa_dict["gof"],
                    nbin        =toa_dict["nbin"],
                    nch         =toa_dict["nch"],
                    chan        =toa_dict["chan"],
                    rcvr        =toa_dict["rcvr"],
                    snr         =toa_dict["snr"],
                    length      =toa_dict["length"],
                    subint      =toa_dict["subint"],
                    dm_corrected  =input["dmCorrected"],
                    minimum_nsubs =input["minimumNsubs"],
                    maximum_nsubs =input["maximumNsubs"],
                    obs_nchan = int(observation.nchan) // int(toa_dict["nch"])
                )
            )
        created_toas = Toa.objects.bulk_create(
            toas_to_create,
            update_conflicts=True,
            unique_fields=[
                "observation",
                "project",
                "dm_corrected",
                # Frequency
                "obs_nchan", # Number of channels
                "chan", # Chan ID
                # Time
                "minimum_nsubs",
                "maximum_nsubs",
                "subint", # Time ID
            ],
            update_fields=[
                "pipeline_run",
                "observation",
                "project",
                "ephemeris",
                "template",
                "archive",
                "freq_MHz",
                "mjd",
                "mjd_err",
                "telescope",
                "fe",
                "be",
                "f",
                "bw",
                "tobs",
                "tmplt",
                "gof",
                "nbin",
                "nch",
                "chan",
                "rcvr",
                "snr",
                "length",
                "subint",
                "dm_corrected",
                "minimum_nsubs",
                "maximum_nsubs",
                "obs_nchan",
            ],
        )
        return CreateToaOutput(toa=created_toas)


class UpdateToa(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ToaInput(required=True)

    toa = graphene.Field(ToaNode)

    @classmethod
    @permission_required("dataportal.add_toa")
    def mutate(cls, self, info, id, input):
        try:
            toa = Toa.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(toa, key, val)
            toa.save()
            return UpdateToa(toa=toa)
        except:
            return UpdateToa(toa=None)


class DeleteToa(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_toa")
    def mutate(cls, self, info, id):
        Toa.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_toa = CreateToa.Field()
    update_toa = UpdateToa.Field()
    delete_toa = DeleteToa.Field()
