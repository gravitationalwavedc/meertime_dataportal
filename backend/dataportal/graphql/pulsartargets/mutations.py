import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Pulsartargets
from .types import PulsartargetsInput, PulsartargetsType


class CreatePulsartarget(graphene.Mutation):
    class Arguments:
        input = PulsartargetsInput(required=True)

    pulsartarget = graphene.Field(PulsartargetsType)

    @classmethod
    @permission_required("dataportal.add_pulsartargets")
    def mutate(cls, self, info, input):
        pulsartarget, _ = Pulsartargets.objects.get_or_create(**input.__dict__)
        return CreatePulsartarget(pulsartarget=pulsartarget)


class UpdatePulsartarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PulsartargetsInput(required=True)

    pulsartarget = graphene.Field(PulsartargetsType)

    @classmethod
    @permission_required("dataportal.add_pulsartargets")
    def mutate(cls, self, info, id, input):
        try:
            pulsartarget = Pulsartargets.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(pulsartarget, key, val)
            pulsartarget.save()
            return UpdatePulsartarget(pulsartarget=pulsartarget)
        except:
            return UpdatePulsartarget(pulsartarget=None)


class DeletePulsartarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_pulsartargets")
    def mutate(cls, self, info, id):
        Pulsartargets.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_pulsartarget = CreatePulsartarget.Field()
    update_pulsartarget = UpdatePulsartarget.Field()
    delete_pulsartarget = DeletePulsartarget.Field()
