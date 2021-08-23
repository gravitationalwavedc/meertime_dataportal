import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateFolding(graphene.Mutation):
    class Arguments:
        input = FoldingsInput(required=True)

    folding = graphene.Field(FoldingsType)

    @classmethod
    @permission_required("dataportal.add_foldings")
    def mutate(cls, self, info, input):
        _folding, _ = Foldings.objects.get_or_create(processing__id=input.processing_id, defaults=input.__dict__)
        return CreateFolding(folding=_folding)


class UpdateFolding(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = FoldingsInput(required=True)

    folding = graphene.Field(FoldingsType)

    @classmethod
    @permission_required("dataportal.add_foldings")
    def mutate(cls, self, info, id, input):
        _folding = Foldings.objects.get(pk=id)
        if _folding:
            for key, val in input.__dict__.items():
                setattr(_folding, key, val)
            _folding.save()
            return UpdateFolding(folding=_folding)
        return UpdateFolding(folding=None)


class DeleteFolding(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    folding = graphene.Field(FoldingsType)

    @classmethod
    @permission_required("dataportal.add_foldings")
    def mutate(cls, self, info, id):
        _folding = Foldings.objects.get(pk=id)
        _folding.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_folding = CreateFolding.Field()
    update_folding = UpdateFolding.Field()
    delete_folding = DeleteFolding.Field()