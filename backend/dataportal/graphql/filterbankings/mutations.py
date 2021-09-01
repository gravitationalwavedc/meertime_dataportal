import graphene
from graphql_jwt.decorators import permission_required

from dataportal.models import Filterbankings
from .types import FilterbankingsInput, FilterbankingsType


class CreateFilterbanking(graphene.Mutation):
    class Arguments:
        input = FilterbankingsInput(required=True)

    filterbanking = graphene.Field(FilterbankingsType)

    @classmethod
    @permission_required("dataportal.add_filterbankings")
    def mutate(cls, self, info, input):
        filterbanking, _ = Filterbankings.objects.get_or_create(**input.__dict__)
        return CreateFilterbanking(filterbanking=filterbanking)


class UpdateFilterbanking(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = FilterbankingsInput(required=True)

    filterbanking = graphene.Field(FilterbankingsType)

    @classmethod
    @permission_required("dataportal.add_filterbankings")
    def mutate(cls, self, info, id, input):
        try:
            filterbanking = Filterbankings.objects.get(pk=id)
            for key, val in input.__dict__.items():
                setattr(filterbanking, key, val)
            filterbanking.save()
            return UpdateFilterbanking(filterbanking=filterbanking)
        except:
            return UpdateFilterbanking(filterbanking=None)


class DeleteFilterbanking(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @classmethod
    @permission_required("dataportal.add_filterbankings")
    def mutate(cls, self, info, id):
        Filterbankings.objects.get(pk=id).delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_filterbanking = CreateFilterbanking.Field()
    update_filterbanking = UpdateFilterbanking.Field()
    delete_filterbanking = DeleteFilterbanking.Field()
