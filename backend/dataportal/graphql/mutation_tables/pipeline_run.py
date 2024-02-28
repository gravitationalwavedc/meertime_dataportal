import graphene
from graphql_jwt.decorators import permission_required

from dataportal.graphql.queries import PipelineRunNode
from dataportal.models import Ephemeris, Observation, PipelineRun, Template


class PipelineRunInput(graphene.InputObjectType):
    observationId = graphene.Int()
    ephemerisId = graphene.Int()
    templateId = graphene.Int()

    pipelineName = graphene.String()
    pipelineDescription = graphene.String()
    pipelineVersion = graphene.String()
    jobState = graphene.String()
    location = graphene.String()
    configuration = graphene.String()

    # DM results
    dm = graphene.Float()
    dmErr = graphene.Float()
    dmEpoch = graphene.Float()
    dmChi2r = graphene.Float()
    dmTres = graphene.Float()

    # Other results
    sn = graphene.Float()
    flux = graphene.Float()
    rm = graphene.Float()
    rmErr = graphene.Float()
    percentRfiZapped = graphene.Float()


class CreatePipelineRun(graphene.Mutation):
    class Arguments:
        input = PipelineRunInput()

    pipeline_run = graphene.Field(PipelineRunNode)

    @classmethod
    @permission_required("dataportal.add_pipeline_run")
    def mutate(cls, self, info, input=None):
        # Get foreign key models
        observation = Observation.objects.get(id=input["observationId"])
        ephemeris = Ephemeris.objects.get(id=input["ephemerisId"])
        if input["templateId"] == -1:
            template = None
        else:
            template = Template.objects.get(id=input["templateId"])

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
            dm_err=input.dmErr,
            dm_epoch=input.dmEpoch,
            dm_chi2r=input.dmChi2r,
            dm_tres=input.dmTres,
            sn=input.sn,
            flux=input.flux,
            rm=input.rm,
            rm_err=input.rmErr,
            percent_rfi_zapped=input.percentRfiZapped,
        )
        return CreatePipelineRun(pipeline_run=pipeline_run)


class UpdatePipelineRun(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PipelineRunInput(required=True)

    pipeline_run = graphene.Field(PipelineRunNode)

    @classmethod
    @permission_required("dataportal.add_pipeline_run")
    def mutate(cls, self, info, id, input=None):
        try:
            pipeline_run = PipelineRun.objects.get(id=id)
            pipeline_run.job_state = input.jobState
            pipeline_run.dm = input.dm
            pipeline_run.dm_err = input.dmErr
            pipeline_run.dm_epoch = input.dmEpoch
            pipeline_run.dm_chi2r = input.dmChi2r
            pipeline_run.dm_tres = input.dmTres
            pipeline_run.sn = input.sn
            pipeline_run.flux = input.flux
            pipeline_run.rm = input.rm
            pipeline_run.rm_err = input.rmErr
            pipeline_run.percent_rfi_zapped = input.percentRfiZapped
            pipeline_run.save()
            return UpdatePipelineRun(pipeline_run=pipeline_run)
        except Exception:
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
