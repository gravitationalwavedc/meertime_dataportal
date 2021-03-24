import graphene
from graphql_jwt.decorators import permission_required
from .types import *

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
        try:
            Pipelineimages.objects.get(processing_id=input.processing_id, rank=input.rank)
            raise GraphQLError("a matching image already exists")
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            raise GraphQLError("Multiple objects match, please update the matching entry/ies")

        _pipeline_image = Pipelineimages.objects.create(
            processing_id=input.processing_id, rank=input.rank, image_type=input.image_type, image=None
        )
        if input.image:
            image_cf = ContentFile(b64decode(input.image))
            _pipeline_image.image.save(f"{input.image_type}.png", image_cf)
        return CreatePipelineimage(pipelineimage=_pipeline_image)


class Mutation(graphene.ObjectType):
    create_pipelineimage = CreatePipelineimage.Field()
