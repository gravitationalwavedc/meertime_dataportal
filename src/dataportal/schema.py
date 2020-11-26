import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required, login_required

from .models import (
    Basebandings,
    Caspsrconfigs,
    Collections,
    Ephemerides,
    Filterbankings,
    Foldings,
    Instrumentconfigs,
    Launches,
    Observations,
    Ptusecalibrations,
    Ptuseconfigs,
    Pipelineimages,
    Pipelines,
    Processingcollections,
    Processings,
    Pulsaraliases,
    Pulsartargets,
    Pulsars,
    Rfis,
    Targets,
    Telescopes,
    Templates,
    Toas,
)

# from ingest.ingest_methods import create_fold_mode, create_search_mode, create_fluxcal, create_ephemeris


class BasebandingsType(DjangoObjectType):
    class Meta:
        model = Basebandings


class CaspsrconfigsType(DjangoObjectType):
    class Meta:
        model = Caspsrconfigs


class CollectionsType(DjangoObjectType):
    class Meta:
        model = Collections


class EphemeridesType(DjangoObjectType):
    class Meta:
        model = Ephemerides


class FilterbankingsType(DjangoObjectType):
    class Meta:
        model = Filterbankings


class FoldingsType(DjangoObjectType):
    class Meta:
        model = Foldings


class InstrumentconfigsType(DjangoObjectType):
    class Meta:
        model = Instrumentconfigs


class LaunchesType(DjangoObjectType):
    class Meta:
        model = Launches


class ObservationsType(DjangoObjectType):
    class Meta:
        model = Observations


class PtusecalibrationsType(DjangoObjectType):
    class Meta:
        model = Ptusecalibrations


class PtuseconfigsType(DjangoObjectType):
    class Meta:
        model = Ptuseconfigs


class PipelineimagesType(DjangoObjectType):
    class Meta:
        model = Pipelineimages


class PipelinesType(DjangoObjectType):
    class Meta:
        model = Pipelines


class ProcessingcollectionsType(DjangoObjectType):
    class Meta:
        model = Processingcollections


class ProcessingsType(DjangoObjectType):
    class Meta:
        model = Processings


class PulsaraliasesType(DjangoObjectType):
    class Meta:
        model = Pulsaraliases


class PulsartargetsType(DjangoObjectType):
    class Meta:
        model = Pulsartargets


class PulsarsType(DjangoObjectType):
    class Meta:
        model = Pulsars


class RfisType(DjangoObjectType):
    class Meta:
        model = Rfis


class TargetsType(DjangoObjectType):
    class Meta:
        model = Targets


class TelescopesType(DjangoObjectType):
    class Meta:
        model = Telescopes


class TemplatesType(DjangoObjectType):
    class Meta:
        model = Templates


class ToasType(DjangoObjectType):
    class Meta:
        model = Toas


class Query(graphene.ObjectType):
    basebandings = graphene.List(BasebandingsType)
    caspsrconfigs = graphene.List(CaspsrconfigsType)
    collections = graphene.List(CollectionsType)
    ephemerides = graphene.List(EphemeridesType)
    filterbankings = graphene.List(FilterbankingsType)
    foldings = graphene.List(FoldingsType)
    instrumentconfigs = graphene.List(InstrumentconfigsType)
    launches = graphene.List(LaunchesType)
    observations = graphene.List(ObservationsType)
    ptusecalibrations = graphene.List(PtusecalibrationsType)
    ptuseconfigs = graphene.List(PtuseconfigsType)
    pipelineimages = graphene.List(PipelineimagesType)
    pipelines = graphene.List(PipelinesType)
    processingcollections = graphene.List(ProcessingcollectionsType)
    processings = graphene.List(ProcessingsType)
    pulsaraliases = graphene.List(PulsaraliasesType)
    pulsartargets = graphene.List(PulsartargetsType)
    pulsars = graphene.List(PulsarsType)
    rfis = graphene.List(RfisType)
    targets = graphene.List(TargetsType)
    telescopes = graphene.List(TelescopesType)
    templates = graphene.List(TemplatesType)
    toas = graphene.List(ToasType)

    @login_required
    def resolve_basebandings(cls, info, **kwargs):
        return Basebandings.objects.all()

    @login_required
    def resolve_caspsrconfigs(cls, info, **kwargs):
        return Caspsrconfigs.objects.all()

    @login_required
    def resolve_collections(cls, info, **kwargs):
        return Collections.objects.all()

    @login_required
    def resolve_ephemerides(cls, info, **kwargs):
        return Ephemerides.objects.all()

    @login_required
    def resolve_filterbankings(cls, info, **kwargs):
        return Filterbankings.objects.all()

    @login_required
    def resolve_foldings(cls, info, **kwargs):
        return Foldings.objects.all()

    @login_required
    def resolve_instrumentconfigs(cls, info, **kwargs):
        return Instrumentconfigs.objects.all()

    @login_required
    def resolve_launches(cls, info, **kwargs):
        return Launches.objects.all()

    @login_required
    def resolve_observations(cls, info, **kwargs):
        return Observations.objects.all()

    @login_required
    def resolve_ptusecalibrations(cls, info, **kwargs):
        return Ptusecalibrations.objects.all()

    @login_required
    def resolve_ptuseconfigs(cls, info, **kwargs):
        return Ptuseconfigs.objects.all()

    @login_required
    def resolve_pipelineimages(cls, info, **kwargs):
        return Pipelineimages.objects.all()

    @login_required
    def resolve_pipelines(cls, info, **kwargs):
        return Pipelines.objects.all()

    @login_required
    def resolve_processingcollections(cls, info, **kwargs):
        return Processingcollections.objects.all()

    @login_required
    def resolve_processings(cls, info, **kwargs):
        return Processings.objects.all()

    @login_required
    def resolve_pulsaraliases(cls, info, **kwargs):
        return Pulsaraliases.objects.all()

    @login_required
    def resolve_pulsartargets(cls, info, **kwargs):
        return Pulsartargets.objects.all()

    @login_required
    def resolve_pulsars(cls, info, **kwargs):
        return Pulsars.objects.all()

    @login_required
    def resolve_rfis(cls, info, **kwargs):
        return Rfis.objects.all()

    @login_required
    def resolve_targets(cls, info, **kwargs):
        return Targets.objects.all()

    @login_required
    def resolve_telescopes(cls, info, **kwargs):
        return Telescopes.objects.all()

    @login_required
    def resolve_templates(cls, info, **kwargs):
        return Templates.objects.all()

    @login_required
    def resolve_toas(cls, info, **kwargs):
        return Toas.objects.all()


class CreateTarget(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        raj = graphene.String()
        decj = graphene.String()

    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, name, raj, decj):
        _target, _ = Targets.objects.get_or_create(name=name, raj=raj, decj=decj)
        return CreateTarget(target=_target)


class Mutation(graphene.ObjectType):
    create_target = CreateTarget.Field()
