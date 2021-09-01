import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Pipelineimages
from .types import PipelineimagesInput, PipelineimagesType

from base64 import b64decode
from django.core.files.base import ContentFile

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from graphql import GraphQLError


class CreatePipelineimage(graphene.Mutation):
    class Arguments:
        input = PipelineimagesInput(required=True)

    pipelineimage = graphene.Field(PipelineimagesType)

    @classmethod
    @permission_required("dataportal.add_pipelineimages")
    def mutate(cls, self, info, input):
        pipeline_image = None
        try:
            pipeline_image = Pipelineimages.objects.get(processing_id=input.processing_id, rank=input.rank)
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            raise GraphQLError("Multiple objects match, please update the matching entry/ies")

        if pipeline_image:
            return CreatePipelineimage(pipelineimage=pipeline_image)
        else:
            pipeline_image = Pipelineimages.objects.create(
                processing_id=input.processing_id, rank=input.rank, image_type=input.image_type, image=None
            )
        if input.image:
            image_cf = ContentFile(b64decode(input.image))
            pipeline_image.image.save(f"{input.image_type}.png", image_cf)
        return CreatePipelineimage(pipelineimage=pipeline_image)


class UpdatePipelineimage(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PipelineimagesInput(required=True)

    pipelineimage = graphene.Field(PipelineimagesType)

    @classmethod
    @permission_required("dataportal.add_pipelineimages")
    def mutate(cls, self, info, id, input=None):
        try:
            pipelineimage = Pipelineimages.objects.get(pk=id)
            pipelineimage.processing_id = input.processing_id
            pipelineimage.rank = input.rank
            pipelineimage.image_type = input.image_type
            if input.image:
                image_cf = ContentFile(b64decode(input.image))
                pipelineimage.image.save(f"{input.image_type}.png", image_cf)
            pipelineimage.save()
            return UpdatePipelineimage(pipelineimage=pipelineimage)
        except:
            return UpdatePipelineimage(pipelineimage=None)


class DeletePipelineimage(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_pipelineimages")
    def mutate(cls, self, info, id):
        pipelineimage = Pipelineimages.objects.get(pk=id)
        pipelineimage.image.delete()
        pipelineimage.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_pipelineimage = CreatePipelineimage.Field()
    update_pipelineimage = UpdatePipelineimage.Field()
    delete_pipelineimage = DeletePipelineimage.Field()
