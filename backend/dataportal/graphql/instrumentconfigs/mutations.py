import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Instrumentconfigs
from .types import InstrumentconfigsInput, InstrumentconfigsType
from decimal import Decimal


class CreateInstrumentconfig(graphene.Mutation):
    class Arguments:
        input = InstrumentconfigsInput(required=True)

    instrumentconfig = graphene.Field(InstrumentconfigsType)

    @classmethod
    @permission_required("dataportal.add_instrumentconfigs")
    def mutate(cls, self, info, input):
        # santize the the decimal values due to Django bug
        for field, limits in InstrumentconfigsInput.limits.items():
            deci_str = "1.".ljust(limits["deci"] + 2, "0")
            input.__dict__[field] = input.__dict__[field].quantize(Decimal(deci_str))
        instrumentconfig, _ = Instrumentconfigs.objects.get_or_create(**input.__dict__)
        return CreateInstrumentconfig(instrumentconfig=instrumentconfig)


class UpdateInstrumentconfig(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = InstrumentconfigsInput(required=True)

    instrumentconfig = graphene.Field(InstrumentconfigsType)

    @classmethod
    @permission_required("dataportal.add_instrumentconfigs")
    def mutate(cls, self, info, id, input):
        try:
            instrumentconfig = Instrumentconfigs.objects.get(pk=id)
            for key, val in input.__dict__.items():
                limits = InstrumentconfigsInput.limits.get(key)
                if limits is not None:
                    deci_str = "1.".ljust(limits["deci"] + 2, "0")
                    val = val.quantize(Decimal(deci_str))
                setattr(instrumentconfig, key, val)
            instrumentconfig.save()
            return UpdateInstrumentconfig(instrumentconfig=instrumentconfig)
        except:
            return UpdateInstrumentconfig(instrumentconfig=None)


class DeleteInstrumentconfig(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_instrumentconfigs")
    def mutate(cls, self, info, id):
        Instrumentconfigs.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_instrumentconfig = CreateInstrumentconfig.Field()
    update_instrumentconfig = UpdateInstrumentconfig.Field()
    delete_instrumentconfig = DeleteInstrumentconfig.Field()
