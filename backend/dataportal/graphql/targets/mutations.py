import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Targets
from .types import TargetsInput, TargetsType


class CreateTarget(graphene.Mutation):
    class Arguments:
        input = TargetsInput(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, input):
        ok = True
        target, _ = Targets.objects.get_or_create(**input.__dict__)
        return CreateTarget(ok=ok, target=target)


class UpdateTarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TargetsInput(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, id, input):
        try:
            target = Targets.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(target, key, val)
            target.save()
            return UpdateTarget(target=target)
        except:
            return UpdateTarget(target=None)


class DeleteTarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, id):
        Targets.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_target = CreateTarget.Field()
    update_target = UpdateTarget.Field()
    delete_target = DeleteTarget.Field()
