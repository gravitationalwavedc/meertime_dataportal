import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateBasebanding(graphene.Mutation):
    class Arguments:
        input = BasebandingsInput(required=True)

    basebanding = graphene.Field(BasebandingsType)

    @classmethod
    @permission_required("dataportal.add_basebandings")
    def mutate(cls, self, info, input):
        _basebanding, _ = Basebandings.objects.get_or_create(**input.__dict__)
        return CreateBasebanding(basebanding=_basebanding)


class UpdateBasebanding(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = BasebandingsInput(required=True)

    basebanding = graphene.Field(BasebandingsType)

    @classmethod
    @permission_required("dataportal.add_basebandings")
    def mutate(cls, self, info, id, input):
        _basebanding = Basebandings.objects.get(pk=id)
        if _basebanding:
            for key, val in input.__dict__.items():
                setattr(_basebanding, key, val)
            _basebanding.save()
            return UpdateBasebanding(basebanding=_basebanding)
        return UpdateBasebanding(basebanding=None)


class Mutation(graphene.ObjectType):
    create_basebanding = CreateBasebanding.Field()
    update_basebanding = UpdateBasebanding.Field()
