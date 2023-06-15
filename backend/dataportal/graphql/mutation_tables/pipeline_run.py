import json

import graphene
from graphql_jwt.decorators import permission_required
from graphene_django import DjangoObjectType

from utils.ephemeris import parse_ephemeris_file
from dataportal.models import (
    PipelineRun,
)


class PipelineRunType(DjangoObjectType):
    class Meta:
        model = PipelineRun


class PipelineRunInput(graphene.InputObjectType):
    observationId = graphene.Int(required=True)
    ephemerisLoc  = graphene.String(required=True)
    templateLoc   = graphene.String(required=True)

    pipelineName = graphene.String(required=True)
    pipelineDescription = graphene.String(required=True)
    pipelineVersion = graphene.String(required=True)
    jobState = graphene.String(required=True)
    location = graphene.String(required=True)
    configuration = models.JSONField(blank=True, null=True)

    # ephemeris_download_link = models.URLField(null=True)
    # toas_download_link = models.URLField(null=True)

    # DM results
    dm       = graphene.Float()
    dmErr   = graphene.Float()
    dmEpoch = graphene.Float()
    dmChi2r = graphene.Float()
    dmTres  = graphene.Float()

    # Other results
    sn = graphene.Float()
    flux = graphene.Float()
    rm = graphene.Float()
    percent_rfi_zapped = graphene.Float()


class CreatePipelineRun(graphene.Mutation):
    class Arguments:
        input = PipelineRunInput()

    pipeline_run = graphene.Field(PipelineRunType)

    @classmethod
    @permission_required("dataportal.add_pipeline_run")
    def mutate(cls, self, info, input=None):
        # Get foreign key models
        pulsar      = Pulsar.objects.get(name=input["pulsarName"])
        telescope   = Telescope.objects.get(name=input["telescopeName"])
        project     = Project.objects.get(code=input["projectCode"])
        calibration = Calibration.objects.get(id=input["calibrationId"])

        # Use get_or_create to create the observations with the required fields and everything else put as defaults
        pipeline_run, _ = PipelineRun.objects.get_or_create(
            observation=observation,
            ephemeris=ephemeris,
            template=template,
            pipeline_name=input.pipelineName,
            pipeline_description=input.pipelineName,
            pipeline_version=input.pipelineName,
            created_at = models.DateTimeField()
            created_by = models.CharField(max_length=64)
            job_state = models.CharField(max_length=255, blank=True, null=True)
            location = models.CharField(max_length=255)
            configuration = models.JSONField(blank=True, null=True)

            # DM results
            dm       = models.FloatField(null=True)
            dm_err   = models.FloatField(null=True)
            dm_epoch = models.FloatField(null=True)
            dm_chi2r = models.FloatField(null=True)
            dm_tres  = models.FloatField(null=True)

            # Other results
            sn = models.FloatField(null=True)
            flux = models.FloatField(null=True)
            rm = models.FloatField(null=True)
            percent_rfi_zapped = models.FloatField(null=True)
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
        return CreatePipelineRun(pipeline_run=pipeline_run)


class UpdatePipelineRun(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PipelineRunInput(required=True)

    pipeline_run = graphene.Field(PipelineRunType)

    @classmethod
    @permission_required("dataportal.add_pipeline_run")
    def mutate(cls, self, info, id, input=None):
        try:
            pipeline_run = PipelineRun.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(pipeline_run, key, val)
            pipeline_run.save()
            return UpdatePipelineRun(pipeline_run=pipeline_run)
        except:
            return UpdatePipelineRun(pipeline_run=None)


class DeletePipelineRun(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_pipeline_run")
    def mutate(cls, self, info, id):
        PipelineRun.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    createPipelineRun = CreatePipelineRun.Field()
    updatePipelineRun = UpdatePipelineRun.Field()
    deletePipelineRun = DeletePipelineRun.Field()