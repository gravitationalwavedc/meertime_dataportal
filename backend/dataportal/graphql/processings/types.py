import graphene
from graphene_django import DjangoObjectType

from ...models import Processings


class ProcessingsType(DjangoObjectType):
    class Meta:
        model = Processings


class ProcessingInput(graphene.InputObjectType):
    observation_id = graphene.Int(name="observation_id", required=True)
    pipeline_id = graphene.Int(name="pipeline_id", required=True)
    parent_id = graphene.Int(name="parent_id", required=True)
    embargo_end = graphene.DateTime(name="embargo_end", required=True)
    location = graphene.String(required=True)
    job_state = graphene.JSONString(name="job_state", required=True)
    job_output = graphene.JSONString(name="job_output", required=True)
    results = graphene.JSONString(required=True)
