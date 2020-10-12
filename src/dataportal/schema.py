import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required, login_required

from .models import Observations, Searchmode, Fluxcal, Pulsars, Utcs, Ephemerides, Proposals
from ingest.ingest_methods import create_fold_mode, create_search_mode, create_fluxcal, create_ephemeris


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


class EphemerisType(DjangoObjectType):
    class Meta:
        model = Ephemerides


class ProposalType(DjangoObjectType):
    class Meta:
        model = Proposals


class Query(graphene.ObjectType):
    observations = graphene.List(ObservationsType)
    searchmode = graphene.List(SearchmodeType)
    fluxcal = graphene.List(FluxcalType)
    utcs = graphene.List(UtcsType)
    pulsars = graphene.List(PulsarType)
    ephemeris = graphene.List(EphemerisType)

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

    @login_required
    def resolve_ephemerides(self, info, **kwargs):
        return Ephemerides.objects.all()

    @login_required
    def reslove_proposals(self, info, **kwargs):
        return Proposals.objects.all()


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
        profile = graphene.String()
        phase_vs_time = graphene.String()
        phase_vs_frequency = graphene.String()
        bandpass = graphene.String()
        snr_vs_time = graphene.String()
        update = graphene.Boolean()

    observations = graphene.Field(ObservationsType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(
        cls,
        self,
        info,
        utc,
        jname,
        beam,
        DM,
        snr,
        length,
        nchan,
        nbin,
        nant,
        nant_eff,
        proposal,
        bw,
        frequency,
        profile,
        phase_vs_time,
        phase_vs_frequency,
        bandpass,
        snr_vs_time,
        update,
    ):
        obs = create_fold_mode(
            utc,
            jname,
            beam,
            DM,
            snr,
            length,
            nchan,
            nbin,
            nant,
            nant_eff,
            proposal,
            bw,
            frequency,
            profile,
            phase_vs_time,
            phase_vs_frequency,
            bandpass,
            snr_vs_time,
            update,
        )
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


class CreateEphemeris(graphene.Mutation):
    class Arguments:
        jname = graphene.String()
        updated_at = graphene.String()
        ephemeris = graphene.String()
        comment = graphene.String()

    ephemeris = graphene.Field(EphemerisType)

    @classmethod
    @permission_required("dataportal.add_observations")
    def mutate(cls, self, info, jname, updated_at, ephemeris, comment):
        eph = create_ephemeris(jname, updated_at, ephemeris, comment)
        return CreateEphemeris(ephemeris=eph)


class Mutation(graphene.ObjectType):
    create_observation = CreateObservation.Field()
    create_searchmode = CreateSearchmode.Field()
    create_fluxcal = CreateFluxcal.Field()
    create_ephemeris = CreateEphemeris.Field()
