import graphene
from graphql_jwt.decorators import permission_required
from .types import *


class CreateFilterbanking(graphene.Mutation):
    class Arguments:
        input = FilterbankingsInput(required=True)

    filterbanking = graphene.Field(FilterbankingsType)

    @classmethod
    @permission_required("dataportal.add_filterbankings")
    def mutate(cls, self, info, input):
        _filterbanking, _ = Filterbankings.objects.get_or_create(**input.__dict__)
        return CreateFilterbanking(filterbanking=_filterbanking)


class UpdateFilterbanking(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = FilterbankingsInput(required=True)

    filterbanking = graphene.Field(FilterbankingsType)

    @classmethod
    @permission_required("dataportal.add_filterbankings")
    def mutate(cls, self, info, id, input):
        _filterbanking = Filterbankings.objects.get(pk=id)
        if _filterbanking:
            for key, val in input.__dict__.items():
                setattr(_filterbanking, key, val)
            _filterbanking.save()
            return UpdateFilterbanking(filterbanking=_filterbanking)
        return UpdateFilterbanking(filterbanking=None)


class Mutation(graphene.ObjectType):
    create_filterbanking = CreateFilterbanking.Field()
    update_filterbanking = UpdateFilterbanking.Field()
