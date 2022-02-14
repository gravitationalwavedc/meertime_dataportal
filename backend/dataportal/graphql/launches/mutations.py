import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Launches
from .types import LaunchesInput, LaunchesType


class CreateLaunch(graphene.Mutation):
    class Arguments:
        input = LaunchesInput(required=True)

    launch = graphene.Field(LaunchesType)

    @classmethod
    @permission_required("dataportal.add_launches")
    def mutate(cls, self, info, input):
        launch, _ = Launches.objects.get_or_create(**input.__dict__)
        return CreateLaunch(launch=launch)


class UpdateLaunch(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = LaunchesInput(required=True)

    launch = graphene.Field(LaunchesType)

    @classmethod
    @permission_required("dataportal.add_launches")
    def mutate(cls, self, info, id, input):
        try:
            launch = Launches.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(launch, key, val)
            launch.save()
            return UpdateLaunch(launch=launch)
        except:
            return UpdateLaunch(launch=None)


class DeleteLaunch(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    launch = graphene.Field(LaunchesType)

    @classmethod
    @permission_required("dataportal.add_launches")
    def mutate(cls, self, info, id):
        Launches.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_launch = CreateLaunch.Field()
    update_launch = UpdateLaunch.Field()
    delete_launch = DeleteLaunch.Field()
