import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateCollection(graphene.Mutation):
    class Arguments:
        input = CollectionsInput(required=True)

    collection = graphene.Field(CollectionsType)

    @classmethod
    @permission_required("dataportal.add_collections")
    def mutate(cls, self, info, input):
        _collection, _ = Collections.objects.get_or_create(**input.__dict__)
        return CreateCollection(collection=_collection)


class UpdateCollection(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CollectionsInput(required=True)

    collection = graphene.Field(CollectionsType)

    @classmethod
    @permission_required("dataportal.add_collections")
    def mutate(cls, self, info, id, input):
        _collection = Collections.objects.get(pk=id)
        if _collection:
            for key, val in input.__dict__.items():
                setattr(_collection, key, val)
            _collection.save()
            return UpdateCollection(collection=_collection)
        return UpdateCollection(collection=None)


class DeleteCollection(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    collection = graphene.Field(CollectionsType)

    @classmethod
    @permission_required("dataportal.add_collections")
    def mutate(cls, self, info, id):
        _collection = Collections.objects.get(pk=id)
        _collection.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_collection = CreateCollection.Field()
    update_collection = UpdateCollection.Field()
    delete_collection = DeleteCollection.Field()
