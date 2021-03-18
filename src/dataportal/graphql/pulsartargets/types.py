from graphene_django import DjangoObjectType
import graphene
from ...models import Pulsartargets


class PulsartargetsType(DjangoObjectType):
    class Meta:
        model = Pulsartargets


class PulsartargetsInput(graphene.InputObjectType):
    pulsar_id = graphene.Int(name="pulsar_id", required=True)
    target_id = graphene.Int(name="target_id", required=True)
