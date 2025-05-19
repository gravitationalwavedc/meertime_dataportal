import graphene
import graphql_jwt
from django.conf import settings

from dataportal.graphql import mutations as dataportal_mutations
from dataportal.graphql import queries as dataportal_queries
from user_manage.graphql import mutations as user_manage_mutations
from user_manage.graphql.types import UserType


class Query(dataportal_queries.Query, graphene.ObjectType):
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


class Mutation(
    dataportal_mutations.Mutation,
    user_manage_mutations.Mutation,
    graphene.ObjectType,
):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
