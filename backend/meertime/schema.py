import graphene

from dataportal.graphql import mutations as dataportal_mutations
from dataportal.graphql import queries as dataportal_queries
from user_manage.graphql import mutations as user_manage_mutations


class Query(dataportal_queries.Query, graphene.ObjectType):
    pass


class Mutation(
    dataportal_mutations.Mutation,
    user_manage_mutations.Mutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
