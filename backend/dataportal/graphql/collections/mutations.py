import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Collections
from .types import CollectionsInput, CollectionsType


class CreateCollection(graphene.Mutation):
    class Arguments:
        input = CollectionsInput(required=True)

    collection = graphene.Field(CollectionsType)

    @classmethod
    @permission_required("dataportal.add_collections")
    def mutate(cls, self, info, input):
        collection, _ = Collections.objects.get_or_create(**input.__dict__)
        return CreateCollection(collection=collection)


class UpdateCollection(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = CollectionsInput(required=True)

    collection = graphene.Field(CollectionsType)

    @classmethod
    @permission_required("dataportal.add_collections")
    def mutate(cls, self, info, id, input):
        try:
            collection = Collections.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(collection, key, val)
            collection.save()
            return UpdateCollection(collection=collection)
        except:
            return UpdateCollection(collection=None)


class DeleteCollection(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_collections")
    def mutate(cls, self, info, id):
        Collections.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_collection = CreateCollection.Field()
    update_collection = UpdateCollection.Field()
    delete_collection = DeleteCollection.Field()
