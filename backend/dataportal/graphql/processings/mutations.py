import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Processings
from .types import ProcessingInput, ProcessingsType


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
        try:
            processing = Processings.objects.get(pk=id)
            for val, key in input.__dict__.items():
                setattr(processing, val, key)
            processing.save()
            return UpdateProcessing(processing=processing)
        except:
            return UpdateProcessing(processing=None)


class DeleteProcessing(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_processings")
    def mutate(cls, self, info, id):
        Processings.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_processing = CreateProcessing.Field()
    update_processing = UpdateProcessing.Field()
    delete_processing = DeleteProcessing.Field()
