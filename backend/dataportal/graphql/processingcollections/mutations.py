import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Processingcollections
from .types import ProcessingcollectionsInput, ProcessingcollectionsType


class CreateProcessingcollection(graphene.Mutation):
    class Arguments:
        input = ProcessingcollectionsInput(required=True)

    processingcollection = graphene.Field(ProcessingcollectionsType)

    @classmethod
    @permission_required("dataportal.add_processingcollections")
    def mutate(cls, self, info, input):
        processingcollection, _ = Processingcollections.objects.get_or_create(**input.__dict__)
        return CreateProcessingcollection(processingcollection=processingcollection)


class UpdateProcessingcollection(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProcessingcollectionsInput(required=True)

    processingcollection = graphene.Field(ProcessingcollectionsType)

    @classmethod
    @permission_required("dataportal.add_processingcollections")
    def mutate(cls, self, info, id, input):
        try:
            processingcollection = Processingcollections.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(processingcollection, key, val)
            processingcollection.save()
            return UpdateProcessingcollection(processingcollection=processingcollection)
        except:
            return UpdateProcessingcollection(processingcollection=None)


class DeleteProcessingcollection(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_processingcollections")
    def mutate(cls, self, info, id):
        Processingcollections.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_processingcollection = CreateProcessingcollection.Field()
    update_processingcollection = UpdateProcessingcollection.Field()
    delete_processingcollection = DeleteProcessingcollection.Field()
