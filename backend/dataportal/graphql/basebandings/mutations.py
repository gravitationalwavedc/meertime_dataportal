import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Basebandings
from .types import BasebandingsInput, BasebandingsType


class CreateBasebanding(graphene.Mutation):
    class Arguments:
        input = BasebandingsInput(required=True)

    basebanding = graphene.Field(BasebandingsType)

    @classmethod
    @permission_required("dataportal.add_basebandings")
    def mutate(cls, self, info, input):
        basebanding, _ = Basebandings.objects.get_or_create(**input.__dict__)
        return CreateBasebanding(basebanding=basebanding)


class UpdateBasebanding(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = BasebandingsInput(required=True)

    basebanding = graphene.Field(BasebandingsType)

    @classmethod
    @permission_required("dataportal.add_basebandings")
    def mutate(cls, self, info, id, input):
        try:
            basebanding = Basebandings.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(basebanding, key, val)
            basebanding.save()
            return UpdateBasebanding(basebanding=basebanding)
        except:
            return UpdateBasebanding(basebanding=None)


class DeleteBasebanding(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_basebandings")
    def mutate(cls, self, info, id):
        Basebandings.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_basebanding = CreateBasebanding.Field()
    update_basebanding = UpdateBasebanding.Field()
    delete_basebanding = DeleteBasebanding.Field()
