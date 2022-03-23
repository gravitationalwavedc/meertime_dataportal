import graphene
import graphql_jwt
import dataportal.graphql
import web_cache.queries
import user_manage.graphql.queries
import user_manage.graphql.mutations
from django.conf import settings


class Query(dataportal.graphql.Query, web_cache.queries.Query, user_manage.graphql.queries.Query, graphene.ObjectType):
    pass


class ObtainJSONWebToken(graphql_jwt.relay.JSONWebTokenMutation):
    meer_watch_key = graphene.String()

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(meer_watch_key=settings.KRONOS_PAYLOAD)


class Mutation(dataportal.graphql.Mutation, web_cache.mutations.Mutation, user_manage.graphql.mutations.Mutation,
               graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
