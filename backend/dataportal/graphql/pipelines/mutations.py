import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Pipelines
from .types import PipelinesInput, PipelinesType


class CreatePipeline(graphene.Mutation):
    class Arguments:
        input = PipelinesInput(required=True)

    pipeline = graphene.Field(PipelinesType)

    @classmethod
    @permission_required("dataportal.add_pipelines")
    def mutate(cls, self, info, input=None):
        pipeline, _ = Pipelines.objects.get_or_create(
            name=input.name, revision=input.revision, defaults=input.__dict__
        )
        return CreatePipeline(pipeline=pipeline)


class UpdatePipeline(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PipelinesInput(required=True)

    pipeline = graphene.Field(PipelinesType)

    @classmethod
    @permission_required("dataportal.add_pipelines")
    def mutate(cls, self, info, id, input=None):
        try:
            pipeline = Pipelines.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(pipeline, key, val)
            pipeline.save()
            return UpdatePipeline(pipeline=pipeline)
        except:
            return UpdatePipeline(pipeline=None)


class DeletePipeline(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_pipelines")
    def mutate(cls, self, info, id):
        Pipelines.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_pipeline = CreatePipeline.Field()
    update_pipeline = UpdatePipeline.Field()
    delete_pipeline = DeletePipeline.Field()
