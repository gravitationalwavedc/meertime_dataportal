import graphene
import graphql_jwt
import dataportal.schema
import dataportal.relay_queries


class Query(dataportal.schema.Query, dataportal.relay_queries.Query, graphene.ObjectType):
    pass


class Mutation(dataportal.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.relay.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
