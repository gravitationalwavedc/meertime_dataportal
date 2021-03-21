from graphene_django import DjangoObjectType
import graphene
from ...models import Processingcollections


class ProcessingcollectionsType(DjangoObjectType):
    class Meta:
        model = Processingcollections


class ProcessingcollectionsInput(graphene.InputObjectType):
    processing_id = graphene.Int(name="processing_id", required=True)
    collection_id = graphene.Int(name="collection_id", required=True)
