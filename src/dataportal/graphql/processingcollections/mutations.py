import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateProcessingcollection(graphene.Mutation):
    class Arguments:
        input = ProcessingcollectionsInput(required=True)

    processingcollection = graphene.Field(ProcessingcollectionsType)

    @classmethod
    @permission_required("dataportal.add_processingcollections")
    def mutate(cls, self, info, input):
        _processingcollection, _ = Processingcollections.objects.get_or_create(**input.__dict__)
        return CreateProcessingcollection(processingcollection=_processingcollection)


class UpdateProcessingcollection(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProcessingcollectionsInput(required=True)

    processingcollection = graphene.Field(ProcessingcollectionsType)

    @classmethod
    @permission_required("dataportal.add_processingcollections")
    def mutate(cls, self, info, id, input):
        _processingcollection = Processingcollections.objects.get(pk=id)
        if _processingcollection:
            for key, val in input.__dict__.items():
                setattr(_processingcollection, key, val)
            _processingcollection.save()
            return UpdateProcessingcollection(processingcollection=_processingcollection)
        return UpdateProcessingcollection(processingcollection=None)


class Mutation(graphene.ObjectType):
    create_processingcollection = CreateProcessingcollection.Field()
    update_processingcollection = UpdateProcessingcollection.Field()
