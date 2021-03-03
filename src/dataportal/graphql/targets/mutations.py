import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateTarget(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        raj = graphene.String(required=True)
        decj = graphene.String(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, name, raj, decj):
        ok = True
        _target, _ = Targets.objects.get_or_create(name=name, raj=raj, decj=decj)
        return CreateTarget(ok=ok, target=_target)


class UpdateTarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        raj = graphene.String(required=True)
        decj = graphene.String(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, id, name, raj, decj):
        _target = Targets.objects.get(pk=id)
        if _target:
            _target.name = name
            _target.raj = raj
            _target.decj = decj
            return UpdateTarget(target=_target)
        return UpdateTarget(target=None)


class Mutation(graphene.ObjectType):
    create_target = CreateTarget.Field()
    update_target = UpdateTarget.Field()
