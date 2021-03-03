import graphene
import graphql_jwt
import dataportal.graphql


# class Query(dataportal.schema.Query, graphene.ObjectType):
class Query(dataportal.graphql.Query, graphene.ObjectType):
    pass


class Mutation(dataportal.graphql.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.relay.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
