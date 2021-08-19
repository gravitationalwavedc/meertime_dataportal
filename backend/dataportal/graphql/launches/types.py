from graphene_django import DjangoObjectType
import graphene
from ...models import Launches


class LaunchesType(DjangoObjectType):
    class Meta:
        model = Launches


class LaunchesInput(graphene.InputObjectType):
    pipeline_id = graphene.Int(name="pipeline_id", required=True)
    parent_pipeline_id = graphene.Int(name="parent_pipeline_id", required=True)
    pulsar_id = graphene.Int(name="pulsar_id", required=True)
