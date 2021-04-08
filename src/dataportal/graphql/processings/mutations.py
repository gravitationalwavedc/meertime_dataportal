import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateProcessing(graphene.Mutation):
    class Arguments:
        input = ProcessingInput(required=True)

    processing = graphene.Field(ProcessingsType)

    @classmethod
    @permission_required("dataportal.add_processings")
    def mutate(cls, self, info, input=None):
        if input.parent_id == -1:
            input.parent_id = None
        _processing, _ = Processings.objects.get_or_create(**input.__dict__)
        return CreateProcessing(processing=_processing)


class UpdateProcessing(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProcessingInput(required=True)

    processing = graphene.Field(ProcessingsType)

    @classmethod
    @permission_required("dataportal.add_processings")
    def mutate(cls, self, info, id, input=None):
        _processing = Processings.objects.get(pk=id)
        if _processing:
            for val, key in input.__dict__.items():
                setattr(_processing, val, key)
            _processing.save()
            return UpdateProcessing(processing=_processing)
        return UpdateProcessing(processing=None)


class Mutation(graphene.ObjectType):
    create_processing = CreateProcessing.Field()
    update_processing = UpdateProcessing.Field()
