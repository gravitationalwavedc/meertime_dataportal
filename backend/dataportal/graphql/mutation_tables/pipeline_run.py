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
    observationId = graphene.Int()
    ephemerisId   = graphene.Int()
    templateId    = graphene.Int()

    pipelineName = graphene.String()
    pipelineDescription = graphene.String()
    pipelineVersion = graphene.String()
    jobState = graphene.String()
    location = graphene.String()
    configuration = graphene.String()

    # DM results
    dm       = graphene.Float()
    dmErr   = graphene.Float()
    dmEpoch = graphene.Float()
    dmChi2r = graphene.Float()
    dmTres  = graphene.Float()

    # Other results
    sn   = graphene.Float()
    flux = graphene.Float()
    rm   = graphene.Float()
    percentRfiZapped = graphene.Float()


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

        # Create what is likely the initial pipeline run setup
        pipeline_run = PipelineRun.objects.create(
            observation=observation,
            ephemeris=ephemeris,
            template=template,
            pipeline_name=input.pipelineName,
            pipeline_description=input.pipelineDescription,
            pipeline_version=input.pipelineVersion,
            job_state=input.jobState,
            location=input.location,
            configuration=input.configuration,
            # The results will likely not be set when the pipeline run is created
            dm=input.dm,
            dm_err=input.dm_err,
            dm_epoch=input.dm_epoch,
            dm_chi2r=input.dm_chi2r,
            dm_tres=input.dm_tres,
            sn=input.sn,
            flux=input.flux,
            rm=input.rm,
            percent_rfi_zapped=input.percent_rfi_zapped,
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