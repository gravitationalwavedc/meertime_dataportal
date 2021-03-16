import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreatePulsartarget(graphene.Mutation):
    class Arguments:
        pulsar_id = graphene.Int(name="pulsar", required=True)
        target_id = graphene.Int(name="target", required=True)

    pulsartarget = graphene.Field(PulsartargetsType)

    @classmethod
    @permission_required("dataportal.add_pulsartargets")
    def mutate(cls, self, info, pulsar_id, target_id):
        _pulsartarget, _ = Pulsartargets.objects.get_or_create(pulsar_id=pulsar_id, target_id=target_id)
        return CreatePulsartarget(pulsartarget=_pulsartarget)


class Mutation(graphene.ObjectType):
    create_pulsartarget = CreatePulsartarget.Field()
