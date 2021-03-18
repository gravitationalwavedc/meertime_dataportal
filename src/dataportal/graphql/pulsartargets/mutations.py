import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreatePulsartarget(graphene.Mutation):
    class Arguments:
        input = PulsartargetsInput(required=True)

    pulsartarget = graphene.Field(PulsartargetsType)

    @classmethod
    @permission_required("dataportal.add_pulsartargets")
    def mutate(cls, self, info, input):
        _pulsartarget, _ = Pulsartargets.objects.get_or_create(**input.__dict__)
        return CreatePulsartarget(pulsartarget=_pulsartarget)


class UpdatePulsartarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PulsartargetsInput(required=True)

    pulsartarget = graphene.Field(PulsartargetsType)

    @classmethod
    @permission_required("dataportal.add_pulsartargets")
    def mutate(cls, self, info, id, input):
        _pulsartarget = Pulsartargets.objects.get(pk=id)
        if _pulsartarget:
            for key, val in input.__dict__.items():
                setattr(_pulsartarget, key, val)
            _pulsartarget.save()
            return UpdatePulsartarget(pulsartarget=_pulsartarget)
        return UpdatePulsartarget(pulsartarget=None)


class Mutation(graphene.ObjectType):
    create_pulsartarget = CreatePulsartarget.Field()
    update_pulsartarget = UpdatePulsartarget.Field()
