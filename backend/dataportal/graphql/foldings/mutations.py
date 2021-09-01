import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Foldings
from .types import FoldingsInput, FoldingsType


class CreateFolding(graphene.Mutation):
    class Arguments:
        input = FoldingsInput(required=True)

    folding = graphene.Field(FoldingsType)

    @classmethod
    @permission_required("dataportal.add_foldings")
    def mutate(cls, self, info, input):
        folding, _ = Foldings.objects.get_or_create(processing__id=input.processing_id, defaults=input.__dict__)
        return CreateFolding(folding=folding)


class UpdateFolding(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = FoldingsInput(required=True)

    folding = graphene.Field(FoldingsType)

    @classmethod
    @permission_required("dataportal.add_foldings")
    def mutate(cls, self, info, id, input):
        try:
            folding = Foldings.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(folding, key, val)
            folding.save()
            return UpdateFolding(folding=folding)
        except:
            return UpdateFolding(folding=None)


class DeleteFolding(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_foldings")
    def mutate(cls, self, info, id):
        Foldings.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_folding = CreateFolding.Field()
    update_folding = UpdateFolding.Field()
    delete_folding = DeleteFolding.Field()
