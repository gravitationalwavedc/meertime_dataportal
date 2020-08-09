import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required

from .models import Observations, Pulsars, Utcs
from ingest.ingest import create_fold_mode


class ObservationsType(DjangoObjectType):
    class Meta:
        model = Observations


class UtcsType(DjangoObjectType):
    class Meta:
        model = Utcs


class PulsarType(DjangoObjectType):
    class Meta:
        model = Pulsars


class Query(graphene.ObjectType):
    observations = graphene.List(ObservationsType)
    utcs = graphene.List(UtcsType)
    pulsars = graphene.List(PulsarType)

    def resolve_observations(self, info, **kwargs):
        return Observations.objects.all()

    def resolve_pulsars(self, info, **kwargs):
        return Pulsars.objects.all()

    def resolve_utcs(self, info, **kwargs):
        return Utcs.objects.all()


class CreateObservation(graphene.Mutation):
    class Arguments:
        utc = graphene.String()
        jname = graphene.String()
        beam = graphene.Int()
        DM = graphene.Float()
        snr = graphene.Float()
        length = graphene.Float()
        nchan = graphene.Int()
        nbin = graphene.Int()
        nant = graphene.Int()
        nant_eff = graphene.Int()
        proposal = graphene.String()
        bw = graphene.Float()
        frequency = graphene.Float()

    observations = graphene.Field(ObservationsType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(
        cls, self, info, utc, jname, beam, DM, snr, length, nchan, nbin, nant, nant_eff, proposal, bw, frequency
    ):
        obs = create_fold_mode(utc, jname, beam, DM, snr, length, nchan, nbin, nant, nant_eff, proposal, bw, frequency)
        return CreateObservation(observations=obs)


class Mutation(graphene.ObjectType):
    create_observation = CreateObservation.Field()
