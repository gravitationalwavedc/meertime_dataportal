import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreatePipeline(graphene.Mutation):
    class Arguments:
        input = PipelinesInput(required=True)

    pipeline = graphene.Field(PipelinesType)

    @classmethod
    @permission_required("dataportal.add_pipelines")
    def mutate(cls, self, info, input=None):
        _pipeline, _ = Pipelines.objects.get_or_create(
            name=input.name,
            description=input.description,
            revision=input.revision,
            created_at=input.createdAt,
            created_by=input.createdBy,
            configuration=input.configuration,
        )
        return CreatePipeline(pipeline=_pipeline)


class UpdatePipeline(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PipelinesInput(required=True)

    pipeline = graphene.Field(PipelinesType)

    @classmethod
    @permission_required("dataportal.add_pipelines")
    def mutate(cls, self, info, id, input=None):
        _pipeline = Pipelines.objects.get(pk=id)
        if _pipeline:
            _pipeline.id = id
            _pipeline.name = input.name
            _pipeline.description = input.description
            _pipeline.revision = input.revision
            _pipeline.created_at = input.createdAt
            _pipeline.created_by = input.createdBy
            _pipeline.configuration = input.configuration
            return UpdatePipeline(pipeline=_pipeline)
        return UpdatePipeline(pipeline=None)


class Mutation(graphene.ObjectType):
    create_pipeline = CreatePipeline.Field()
    update_pipeline = UpdatePipeline.Field()
