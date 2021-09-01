import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Toas
from .types import ToasInput, ToasType
from decimal import Decimal


class CreateToa(graphene.Mutation):
    class Arguments:
        input = ToasInput(required=True)

    toa = graphene.Field(ToasType)

    @classmethod
    @permission_required("dataportal.add_toas")
    def mutate(cls, self, info, input):
        toa, _ = Toas.objects.get_or_create(**input.__dict__)
        return CreateToa(toa=toa)


class UpdateToa(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ToasInput(required=True)

    toa = graphene.Field(ToasType)

    @classmethod
    @permission_required("dataportal.add_toas")
    def mutate(cls, self, info, id, input):
        try:
            toa = Toas.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(toa, key, val)
            toa.save()
            return UpdateToa(toa=toa)
        except:
            return UpdateToa(toa=None)


class DeleteToa(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_toas")
    def mutate(cls, self, info, id):
        Toas.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_toa = CreateToa.Field()
    update_toa = UpdateToa.Field()
    delete_toa = DeleteToa.Field()
