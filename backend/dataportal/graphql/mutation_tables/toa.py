import graphene
from graphql_jwt.decorators import permission_required
from graphql import GraphQLError

from dataportal.models import Toa, PipelineRun, Ephemeris, Template
from dataportal.graphql.queries import ToaNode
from utils.toa import toa_line_to_dict, toa_dict_to_line


class ToaInput(graphene.InputObjectType):
    # foreign keys
    pipelineRunId = graphene.Int(required=True)
    ephemerisId   = graphene.Int(required=True)
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
        ephemeris    = Ephemeris.objects.get(id=input["ephemerisId"])
        template     = Template.objects.get(id=input["templateId"])

        created_toas = []
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
            toa = Toa.objects.create(
                pipeline_run=pipeline_run,
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
            )
            created_toas.append(toa)
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
