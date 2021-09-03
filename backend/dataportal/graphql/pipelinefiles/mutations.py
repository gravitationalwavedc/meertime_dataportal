import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Pipelinefiles
from .types import PipelinefilesInput, PipelinefilesType

from base64 import b64decode
from django.core.files.base import ContentFile

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from graphql import GraphQLError


class CreatePipelinefile(graphene.Mutation):
    class Arguments:
        input = PipelinefilesInput(required=True)

    pipelinefile = graphene.Field(PipelinefilesType)

    @classmethod
    @permission_required("dataportal.add_pipelinefiles")
    def mutate(cls, self, info, input):
        pipelinefile = None
        try:
            pipelinefile = Pipelinefiles.objects.get(processing_id=input.processing_id, file_type=input.file_type)
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            raise GraphQLError("Multiple objects match, please update the matching entry/ies")

        if pipelinefile:
            return CreatePipelinefile(pipelinefile=pipelinefile)
        else:
            pipelinefile = Pipelinefiles.objects.create(
                processing_id=input.processing_id, file_type=input.file_type, file=None
            )
        if input.file:
            file_cf = ContentFile(b64decode(input.file))
            pipelinefile.file.save(input.file_name, file_cf)
        return CreatePipelinefile(pipelinefile=pipelinefile)


class UpdatePipelinefile(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PipelinefilesInput(required=True)

    pipelinefile = graphene.Field(PipelinefilesType)

    @classmethod
    @permission_required("dataportal.add_pipelinefiles")
    def mutate(cls, self, info, id, input=None):
        try:
            pipelinefile = Pipelinefiles.objects.get(pk=id)
            pipelinefile.processing_id = input.processing_id
            pipelinefile.file_type = input.file_type
            if input.file:
                file_cf = ContentFile(b64decode(input.file))
                pipelinefile.file.save(input.file_name, file_cf)
            pipelinefile.save()
            return UpdatePipelinefile(pipelinefile=pipelinefile)
        except:
            return UpdatePipelinefile(pipelinefile=None)


class DeletePipelinefile(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_pipelinefiles")
    def mutate(cls, self, info, id):
        pipelinefile = Pipelinefiles.objects.get(pk=id)
        pipelinefile.file.delete()
        pipelinefile.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_pipelinefile = CreatePipelinefile.Field()
    update_pipelinefile = UpdatePipelinefile.Field()
    delete_pipelinefile = DeletePipelinefile.Field()
