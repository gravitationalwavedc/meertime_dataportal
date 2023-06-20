import json

import graphene
from graphql_jwt.decorators import permission_required
from graphene_django import DjangoObjectType

from utils.ephemeris import parse_ephemeris_file
from dataportal.models import (
    PipelineRun,
    Observation,
    Ephemeris,
    Template,
)


class PipelineRunType(DjangoObjectType):
    class Meta:
        model = PipelineRun


class PipelineRunInput(graphene.InputObjectType):
    observationId = graphene.Int(required=True)
    ephemerisId   = graphene.Int(required=True)
    templateId    = graphene.Int(required=True)

    pipelineName = graphene.String(required=True)
    pipelineDescription = graphene.String(required=True)
    pipelineVersion = graphene.String(required=True)
    jobState = graphene.String(required=True)
    location = graphene.String(required=True)
    configuration = graphene.String(required=True)

    # DM results
    dm       = graphene.Float()
    dm_err   = graphene.Float()
    dm_epoch = graphene.Float()
    dm_chi2r = graphene.Float()
    dm_tres  = graphene.Float()

    # Other results
    sn   = graphene.Float()
    flux = graphene.Float()
    rm   = graphene.Float()
    percent_rfi_zapped = graphene.Float()


class CreatePipelineRun(graphene.Mutation):
    class Arguments:
        input = PipelineRunInput()

    pipeline_run = graphene.Field(PipelineRunType)

    @classmethod
    @permission_required("dataportal.add_pipeline_run")
    def mutate(cls, self, info, input=None):
        # Get foreign key models
        observation = Observation.objects.get(id=input["observationId"])
        ephemeris   = Ephemeris.objects.get(id=input["ephemerisId"])
        template    = Template.objects.get(id=input["templateId"])

        # Load the results JSON string into a dictionary
        results = json.loads(input.results)
        if results:
            # Unpack data
            dm = results.dm
            dm_err = results.dm_err
            dm_epoch = results.dm_epoch
            dm_chi2r = results.dm_chi2r
            dm_tres = results.dm_tres
            sn = results.sn
            flux = results.flux
            rm = results.rm
            percent_rfi_zapped = results.percent_rfi_zapped
        else:
            # None is empty dict given
            dm = None
            dm_err = None
            dm_epoch = None
            dm_chi2r = None
            dm_tres = None
            sn = None
            flux = None
            rm = None
            percent_rfi_zapped = None


        # Create what is likely the initial pipeline run setup
        pipeline_run, _ = PipelineRun.objects.create(
            observation=observation,
            ephemeris=ephemeris,
            template=template,
            pipeline_name=input.pipelineName,
            pipeline_description=input.pipelineDescription,
            pipeline_version=input.pipelineVersion,
            job_state=input.jobState,
            location=input.location,
            configuration=json.load(input.configuration),
            # The results will likely not be set when the pipeline run is created
            dm=dm,
            dm_err=dm_err,
            dm_epoch=dm_epoch,
            dm_chi2r=dm_chi2r,
            dm_tres=dm_tres,
            sn=sn,
            flux=flux,
            rm=rm,
            percent_rfi_zapped=percent_rfi_zapped,
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