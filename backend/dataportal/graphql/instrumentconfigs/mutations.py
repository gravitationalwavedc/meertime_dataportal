import graphene
from graphql_jwt.decorators import permission_required
from .types import *
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
        _instrumentconfig, _ = Instrumentconfigs.objects.get_or_create(**input.__dict__)
        return CreateInstrumentconfig(instrumentconfig=_instrumentconfig)


class UpdateInstrumentconfig(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = InstrumentconfigsInput(required=True)

    instrumentconfig = graphene.Field(InstrumentconfigsType)

    @classmethod
    @permission_required("dataportal.add_instrumentconfigs")
    def mutate(cls, self, info, id, input):
        _instrumentconfig = Instrumentconfigs.objects.get(pk=id)
        if _instrumentconfig:
            for key, val in input.__dict__.items():
                setattr(_instrumentconfig, key, val)
            _instrumentconfig.save()
            return UpdateInstrumentconfig(instrumentconfig=_instrumentconfig)
        return UpdateInstrumentconfig(instrumentconfig=None)


class DeleteInstrumentconfig(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    instrumentconfig = graphene.Field(InstrumentconfigsType)

    @classmethod
    @permission_required("dataportal.add_instrumentconfigs")
    def mutate(cls, self, info, id):
        _instrumentconfig = Instrumentconfigs.objects.get(pk=id)
        _instrumentconfig.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_instrumentconfig = CreateInstrumentconfig.Field()
    update_instrumentconfig = UpdateInstrumentconfig.Field()
    delete_instrumentconfig = DeleteInstrumentconfig.Field()
