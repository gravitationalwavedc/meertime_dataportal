import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import (
    PipelineFile,
)
from dataportal.graphql.queries import PipelineFileNode



class PipelineFileInput(graphene.InputObjectType):
    pulsar_name   = graphene.String(required=True)
    project_code  = graphene.String(required=True)
    band          = graphene.String(required=True)



class DeletePipelineFile(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    pipeline_file = graphene.Field(PipelineFileNode)

    @classmethod
    @permission_required("dataportal.delete_pipeline_file")
    def mutate(cls, self, info, id):
        _pipeline_file = PipelineFile.objects.get(pk=id)
        _pipeline_file.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    deletePipelineFile = DeletePipelineFile.Field()
