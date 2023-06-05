import graphene
import graphql_jwt
import dataportal.graphql
import user_manage.graphql.queries
import user_manage.graphql.mutations
import jobcontroller.queries
import jobcontroller.mutations
from django.conf import settings
from user_manage.graphql.types import UserType


class Query(
    dataportal.graphql.Query,
    user_manage.graphql.queries.Query,
    jobcontroller.queries.Query,
    graphene.ObjectType,
):
    pass


class ObtainJSONWebToken(graphql_jwt.relay.JSONWebTokenMutation):
    meer_watch_key = graphene.String()
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(
            meer_watch_key=settings.KRONOS_PAYLOAD,
            user=info.context.user,
        )


<<<<<<< HEAD
class Mutation(
    dataportal.graphql.Mutation,
    user_manage.graphql.mutations.Mutation,
    jobcontroller.mutations.Mutation,
    graphene.ObjectType,
):
=======
class Mutation(dataportal.graphql.Mutation, web_cache.graphql.Query, user_manage.graphql.mutations.Mutation, graphene.ObjectType):
>>>>>>> a56c9f4 (Started simplifying the Pulsar queries)
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
