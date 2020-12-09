import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import permission_required, login_required
from graphene_django.converter import convert_django_field
from django_mysql.models import JSONField


@convert_django_field.register(JSONField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


from .models import (
    Basebandings,
    Collections,
    Ephemerides,
    Filterbankings,
    Foldings,
    Instrumentconfigs,
    Launches,
    Observations,
    Calibrations,
    Pipelineimages,
    Pipelines,
    Processingcollections,
    Processings,
    Projects,
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


class CalibrationsType(DjangoObjectType):
    class Meta:
        model = Calibrations


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


class ProjectsType(DjangoObjectType):
    class Meta:
        model = Projects


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
    collections = graphene.List(CollectionsType)
    ephemerides = graphene.List(EphemeridesType)
    filterbankings = graphene.List(FilterbankingsType)
    foldings = graphene.List(FoldingsType)
    instrumentconfigs = graphene.List(InstrumentconfigsType)
    launches = graphene.List(LaunchesType)
    observations = graphene.List(ObservationsType)
    calibrations = graphene.List(CalibrationsType)
    pipelineimages = graphene.List(PipelineimagesType)

    pipelines = graphene.List(PipelinesType)
    pipelineById = graphene.Field(PipelinesType, id=graphene.Int())
    pipelinesByName = graphene.List(PipelinesType, name=graphene.String())

    processingcollections = graphene.List(ProcessingcollectionsType)
    processings = graphene.List(ProcessingsType)
    projects = graphene.List(ProjectsType)
    pulsaraliases = graphene.List(PulsaraliasesType)
    pulsartargets = graphene.List(PulsartargetsType)

    pulsars = graphene.List(PulsarsType)
    pulsarById = graphene.Field(PulsarsType, id=graphene.Int())
    pulsarsByJname = graphene.List(PulsarsType, jname=graphene.String())

    rfis = graphene.List(RfisType)

    targets = graphene.List(TargetsType)
    targetById = graphene.Field(TargetsType, id=graphene.Int())
    targetsByName = graphene.List(TargetsType, name=graphene.String())

    telescopes = graphene.List(TelescopesType)
    templates = graphene.List(TemplatesType)
    toas = graphene.List(ToasType)

    @login_required
    def resolve_basebandings(cls, info, **kwargs):
        return Basebandings.objects.all()

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
    def resolve_calibrations(cls, info, **kwargs):
        return Calibrations.objects.all()

    @login_required
    def resolve_pipelineimages(cls, info, **kwargs):
        return Pipelineimages.objects.all()

    @login_required
    def resolve_pipelines(cls, info, **kwargs):
        return Pipelines.objects.all()

    @login_required
    def resolve_pipelineById(cls, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Pipelines.objects.get(pk=id)
        return None

    @login_required
    def resolve_pipelinesByName(cls, info, **kwargs):
        name = kwargs.get('name')
        if name is not None:
            return Pipelines.objects.filter(name=name)
        return None

    @login_required
    def resolve_processingcollections(cls, info, **kwargs):
        return Processingcollections.objects.all()

    @login_required
    def resolve_processings(cls, info, **kwargs):
        return Processings.objects.all()

    @login_required
    def resolve_projects(cls, info, **kwargs):
        return Projects.objects.all()

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
    def resolve_pulsarById(cls, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Pulsars.objects.get(pk=id)
        return None

    @login_required
    def resolve_pulsarsByJname(cls, info, **kwargs):
        jname = kwargs.get('jname')
        if jname is not None:
            return Pulsars.objects.filter(jname=jname)
        return None

    @login_required
    def resolve_rfis(cls, info, **kwargs):
        return Rfis.objects.all()

    @login_required
    def resolve_targets(cls, info, **kwargs):
        return Targets.objects.all()

    @login_required
    def resolve_targetById(cls, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Targets.objects.get(pk=id)
        return None

    @login_required
    def resolve_targetsByName(cls, info, **kwargs):
        name = kwargs.get('name')
        if name is not None:
            return Targets.objects.filter(name=name)
        return None

    @login_required
    def resolve_telescopes(cls, info, **kwargs):
        return Telescopes.objects.all()

    @login_required
    def resolve_templates(cls, info, **kwargs):
        return Templates.objects.all()

    @login_required
    def resolve_toas(cls, info, **kwargs):
        return Toas.objects.all()


class CreatePulsar(graphene.Mutation):
    class Arguments:
        jname = graphene.String(required=True)
        state = graphene.String(required=True)
        comment = graphene.String(required=True)

    pulsar = graphene.Field(PulsarsType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, jname, state, comment):
        _pulsar, _ = Pulsars.objects.get_or_create(jname=jname, state=state, comment=comment)
        return CreatePulsar(pulsar=_pulsar)


class UpdatePulsar(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        jname = graphene.String(required=True)
        state = graphene.String(required=True)
        comment = graphene.String(required=True)

    pulsar = graphene.Field(PulsarsType)

    @classmethod
    @permission_required("dataportal.add_pulsars")
    def mutate(cls, self, info, id, jname, state, comment):
        ok = False
        _pulsar = Pulsars.objects.get(pk=id)
        if _pulsar:
            _pulsar.jname = jname
            _pulsar.state = state
            _pulsar.comment = comment
            return UpdatePulsar(pulsar=_pulsar)
        return UpdatePulsar(pulsar=None)


class CreateTarget(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        raj = graphene.String(required=True)
        decj = graphene.String(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, name, raj, decj):
        ok = True
        _target, _ = Targets.objects.get_or_create(name=name, raj=raj, decj=decj)
        return CreateTarget(ok=ok, target=_target)


class UpdateTarget(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        raj = graphene.String(required=True)
        decj = graphene.String(required=True)

    ok = graphene.Boolean()
    target = graphene.Field(TargetsType)

    @classmethod
    @permission_required("dataportal.add_targets")
    def mutate(cls, self, info, id, name, raj, decj):
        _target = Targets.objects.get(pk=id)
        if _target:
            _target.name = name
            _target.raj = raj
            _target.decj = decj
            return UpdateTarget(target=_target)
        return UpdateTarget(target=None)


class PipelinesInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    revision = graphene.String(required=True)
    createdAt = graphene.DateTime(required=True)
    createdBy = graphene.String(required=True)
    configuration = graphene.String(required=True)


class CreatePipeline(graphene.Mutation):
    class Arguments:
        input = PipelinesInput(required=True)

    pipeline = graphene.Field(PipelinesType)

    @classmethod
    @permission_required("dataportal.add_pipelines")
    def mutate(cls, self, info, input=None):
        _pipeline, _ = Pipelines.objects.get_or_create(
            name=input.name,
            description=input.description,
            revision=input.revision,
            created_at=input.createdAt,
            created_by=input.createdBy,
            configuration=input.configuration,
        )
        return CreatePipeline(pipeline=_pipeline)


class UpdatePipeline(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PipelinesInput(required=True)

    pipeline = graphene.Field(PipelinesType)

    @classmethod
    @permission_required("dataportal.add_pipelines")
    def mutate(cls, self, info, id, input=None):
        _pipeline = Pipelines.objects.get(pk=id)
        if _pipeline:
            _pipeline.id = id
            _pipeline.name = input.name
            _pipeline.description = input.description
            _pipeline.revision = input.revision
            _pipeline.created_at = input.createdAt
            _pipeline.created_by = input.createdBy
            _pipeline.configuration = input.configuration
            return UpdatePipeline(pipeline=_pipeline)
        return UpdatePipeline(pipeline=None)


class Mutation(graphene.ObjectType):
    create_target = CreateTarget.Field()
    update_target = UpdateTarget.Field()
    create_pulsar = CreatePulsar.Field()
    update_pulsar = UpdatePulsar.Field()
    create_pipeline = CreatePipeline.Field()
    update_pipeline = UpdatePipeline.Field()
