import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateTarget(graphene.Mutation):
    class Arguments:
        input = TargetsInput(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, input):
        ok = True
        _target, _ = Targets.objects.get_or_create(**input.__dict__)
        return CreateTarget(ok=ok, target=_target)


class UpdateTarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = TargetsInput(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, id, input):
        _target = Targets.objects.get(pk=id)
        if _target:
            for key, val in input.__dict__.items():
                setattr(_target, key, val)
            _target.save()
            return UpdateTarget(target=_target)
        return UpdateTarget(target=None)


class DeleteTarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, id):
        _target = Targets.objects.get(pk=id)
        _target.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_target = CreateTarget.Field()
    update_target = UpdateTarget.Field()
    delete_target = DeleteTarget.Field()
