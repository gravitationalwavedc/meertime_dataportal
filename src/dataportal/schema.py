import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required, login_required

from .models import Observations, Searchmode, Fluxcal, Pulsars, Utcs
from ingest.ingest import create_fold_mode, create_search_mode, create_fluxcal


class ObservationsType(DjangoObjectType):
    class Meta:
        model = Observations


class SearchmodeType(DjangoObjectType):
    class Meta:
        model = Searchmode


class FluxcalType(DjangoObjectType):
    class Meta:
        model = Fluxcal


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

    @login_required
    def resolve_observations(self, info, **kwargs):
        return Observations.objects.all()

    @login_required
    def resolve_searchmode(self, info, **kwargs):
        return Searchmode.objects.all()

    @login_required
    def resolve_fluxcal(self, info, **kwargs):
        return Fluxcal.objects.all()

    @login_required
    def resolve_pulsars(self, info, **kwargs):
        return Pulsars.objects.all()

    @login_required
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


class CreateSearchmode(graphene.Mutation):
    class Arguments:
        utc = graphene.String()
        jname = graphene.String()
        beam = graphene.Int()
        RA = graphene.String()
        DEC = graphene.String()
        DM = graphene.Float()
        nbit = graphene.Int()
        nchan = graphene.Int()
        npol = graphene.Int()
        tsamp = graphene.Float()
        nant = graphene.Int()
        nant_eff = graphene.Int()
        proposal = graphene.String()
        length = graphene.Float()
        bw = graphene.Float()
        frequency = graphene.Float()

    searchmode = graphene.Field(SearchmodeType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(
        cls,
        self,
        info,
        utc,
        jname,
        beam,
        RA,
        DEC,
        DM,
        nbit,
        nchan,
        npol,
        tsamp,
        nant,
        nant_eff,
        proposal,
        length,
        bw,
        frequency,
    ):
        obs = create_search_mode(
            utc, jname, beam, RA, DEC, DM, nbit, nchan, npol, tsamp, nant, nant_eff, proposal, length, bw, frequency
        )
        return CreateSearchmode(searchmode=obs)


class CreateFluxcal(graphene.Mutation):
    class Arguments:
        utc = graphene.String()
        jname = graphene.String()
        beam = graphene.Int()
        snr = graphene.Float()
        length = graphene.Float()
        nchan = graphene.Int()
        nbin = graphene.Int()
        nant = graphene.Int()
        nant_eff = graphene.Int()
        proposal = graphene.String()
        bw = graphene.Float()
        frequency = graphene.Float()

    fluxcal = graphene.Field(FluxcalType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, utc, jname, beam, snr, length, nchan, nbin, nant, nant_eff, proposal, bw, frequency):
        obs = create_fluxcal(utc, jname, beam, snr, length, nchan, nbin, nant, nant_eff, proposal, bw, frequency)
        return CreateFluxcal(fluxcal=obs)


class Mutation(graphene.ObjectType):
    create_observation = CreateObservation.Field()
    create_searchmode = CreateSearchmode.Field()
    create_fluxcal = CreateFluxcal.Field()
