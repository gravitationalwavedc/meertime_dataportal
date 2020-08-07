import graphene
import dataportal.schema


class Query(dataportal.schema.Query, graphene.ObjectType):
    pass


class Mutation(dataportal.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
