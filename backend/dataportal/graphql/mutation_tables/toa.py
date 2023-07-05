import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required

from dataportal.models import Toa
from datetime import timedelta

from dataportal.models import PipelineRun, Ephemeris, Template
from utils.toa import toa_line_to_dict, toa_dict_to_line


class ToaType(DjangoObjectType):
    class Meta:
        model = Toa


class ToaInput(graphene.InputObjectType):
    # foreign keys
    pipelineRunId = graphene.Int(required=True)
    ephemerisId   = graphene.Int(required=True)
    templateId    = graphene.Int(required=True)

    toaText = graphene.String(required=True)


class CreateToa(graphene.Mutation):
    class Arguments:
        input = ToaInput(required=True)

    toa = graphene.Field(ToaType)

    @classmethod
    @permission_required("dataportal.add_toa")
    def mutate(cls, self, info, input):
        pipeline_run = PipelineRun.objects.get(id=input["pipelineRunId"])
        ephemeris    = Ephemeris.objects.get(id=input["ephemerisId"])
        template     = Template.objects.get(id=input["templateId"])

        toa_lines = input["toaText"].split("\n")
        for toa_line in toa_lines[1:]:
            # Loop over toa lines and turn into a dict
            toa_dict = toa_line_to_dict(toa_line)
            # Revert it back to a line and check it matches before uploading
            output_toa_line = toa_dict_to_line(toa_dict)
            assert toa_line == output_toa_line
            # Upload the toa
            toa = Toa.objects.create(
                pipeline_run=pipeline_run,
                ephemeris   =ephemeris,
                template    =template,
                archive     =toa_dict["archive"],
                freq_MHz    =toa_dict["freqMHz"],
                mjd         =toa_dict["mjd"],
                mjd_err     =toa_dict["mjdErr"],
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
            )
        return CreateToa(toa=toa)


class UpdateToa(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ToaInput(required=True)

    toa = graphene.Field(ToaType)

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
