import graphene
from graphql_jwt.decorators import permission_required

from django.core.management import call_command

REQUIRED_PERMISSIONS = [
    "dataportal.add_foldings",
    "dataportal.add_pulsars",
    "dataportal.add_targets",
    "dataportal.add_sessions",
]


class SyncWebCache(graphene.Mutation):
    ok = graphene.Boolean()

    @classmethod
    @permission_required(REQUIRED_PERMISSIONS)
    def mutate(cls, self, info):
        call_command('sync_web_cache')
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    sync_web_cache = SyncWebCache.Field()
