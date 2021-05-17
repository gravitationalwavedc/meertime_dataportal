import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateLaunch(graphene.Mutation):
    class Arguments:
        input = LaunchesInput(required=True)

    launch = graphene.Field(LaunchesType)

    @classmethod
    @permission_required("dataportal.add_launches")
    def mutate(cls, self, info, input):
        _launch, _ = Launches.objects.get_or_create(**input.__dict__)
        return CreateLaunch(launch=_launch)


class UpdateLaunch(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = LaunchesInput(required=True)

    launch = graphene.Field(LaunchesType)

    @classmethod
    @permission_required("dataportal.add_launches")
    def mutate(cls, self, info, id, input):
        _launch = Launches.objects.get(pk=id)
        if _launch:
            for key, val in input.__dict__.items():
                setattr(_launch, key, val)
            _launch.save()
            return UpdateLaunch(launch=_launch)
        return UpdateLaunch(launch=None)


class DeleteLaunch(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    launch = graphene.Field(LaunchesType)

    @classmethod
    @permission_required("dataportal.add_launchs")
    def mutate(cls, self, info, id):
        _launch = Launches.objects.get(pk=id)
        _launch.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_launch = CreateLaunch.Field()
    update_launch = UpdateLaunch.Field()
    delete_launch = DeleteLaunch.Field()
