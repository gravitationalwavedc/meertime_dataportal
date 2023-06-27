import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required

from dataportal.models import Toa
from datetime import timedelta

from dataportal.models import PipelineRun, Ephemeris, Template


class ToaType(DjangoObjectType):
    class Meta:
        model = Toa


class ToaInput(graphene.InputObjectType):
    # foreign keys
    pipelineRunId = graphene.Int(required=True)
    ephemerisId   = graphene.Int(required=True)
    templateId    = graphene.Int(required=True)

    # toa results
    archive   = graphene.String(required=True)
    freqMHz  = graphene.Float(required=True)
    mjd       = graphene.Decimal(required=True)
    mjdErr   = graphene.Float(required=True)
    telescope = graphene.String(required=True)

    # The flags from the toa file
    fe     = graphene.String()
    be     = graphene.String()
    f      = graphene.String()
    bw     = graphene.Int()
    tobs   = graphene.Int()
    tmplt  = graphene.String()
    gof    = graphene.Float()
    nbin   = graphene.Int()
    nch    = graphene.Int()
    chan   = graphene.Int()
    rcvr   = graphene.String()
    snr    = graphene.Float()
    length = graphene.Int()
    subint = graphene.Int()


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
        toa = Toa.objects.create(
            pipeline_run=pipeline_run,
            ephemeris   =ephemeris,
            template    =template,
            archive     =input["archive"],
            freq_MHz    =input["freqMHz"],
            mjd         =input["mjd"],
            mjd_err     =input["mjdErr"],
            telescope   =input["telescope"],
            fe          =input["fe"],
            be          =input["be"],
            f           =input["f"],
            bw          =input["bw"],
            tobs        =input["tobs"],
            tmplt       =input["tmplt"],
            gof         =input["gof"],
            nbin        =input["nbin"],
            nch         =input["nch"],
            chan        =input["chan"],
            rcvr        =input["rcvr"],
            snr         =input["snr"],
            length      =input["length"],
            subint      =input["subint"],
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
