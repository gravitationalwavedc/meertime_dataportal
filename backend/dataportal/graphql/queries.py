import math

from django.template.defaultfilters import filesizeformat

import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from graphql import GraphQLError

from dataportal.models import Pulsar, Observation, MainProject, Project, Ephemeris, PipelineRun, FoldPulsarSummary, FoldPulsarResult

DATETIME_FILTERS = ["exact", "isnull", "lt", "lte", "gt", "gte", "month", "year", "date"]
NUMERIC_FILTERS = ["exact", "lt", "lte", "gt", "gte"]

class Queries:
    pass


class PulsarNode(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class EphemerisNode(DjangoObjectType):
    class Meta:
        model = Ephemeris
        fields = "__all__"
        filter_fields = {
            "pulsar__id": ["exact"],
            "p0": NUMERIC_FILTERS,
            "dm": NUMERIC_FILTERS,
            "ephemeris_hash": ["exact"],
        }

        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    embargoPeriod = graphene.Int()

    def resolve_embargoPeriod(self, info):
        return self.embargo_period.days

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ProjectNodeConnection(relay.Connection):
    class Meta:
        node = ProjectNode

class ObservationNode(DjangoObjectType):
    class Meta:
        model = Observation
        fields = "__all__"
        filter_fields = {
            "utc_start": DATETIME_FILTERS,
            "duration": NUMERIC_FILTERS,
            "telescope__name": ["exact"],
            "pulsar__name": ["exact"],
            # "project__id": ["exact"],
            "project__short": ["exact"],
        }
        interfaces = (relay.Node,)
    project = graphene.Field(ProjectNode)
    ephemeris = graphene.Field(EphemerisNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ObservationNodeConnection(relay.Connection):
    class Meta:
        node = ObservationNode

class MainProjectNode(DjangoObjectType):
    class Meta:
        model = MainProject
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class PipelineRunNode(DjangoObjectType):
    class Meta:
        model = PipelineRun
        fields = "__all__"
        filter_fields = {
            "id": ["exact"],
            "observation__id": ["exact"],
            "ephemeris__id": ["exact"],
            "template__id": ["exact"],
            "pipeline_name": ["exact"],
            "pipeline_description": ["exact"],
            "pipeline_version": ["exact"],
            "created_at": DATETIME_FILTERS,
            "job_state": ["exact"],
            "location": ["exact"],
            "dm": NUMERIC_FILTERS,
            "dm_err": NUMERIC_FILTERS,
            "dm_epoch": NUMERIC_FILTERS,
            "dm_chi2r": NUMERIC_FILTERS,
            "dm_tres": NUMERIC_FILTERS,
            "sn": NUMERIC_FILTERS,
            "flux": NUMERIC_FILTERS,
            "rm": NUMERIC_FILTERS,
            "percent_rfi_zapped": NUMERIC_FILTERS,
        }

        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class FoldPulsarSummaryNode(DjangoObjectType):
    class Meta:
        model = FoldPulsarSummary
        fields = "__all__"
        filter_fields = {
            "id": ["exact"],
            "pulsar__id": ["exact"],
            "main_project__id": ["exact"],
            "first_observation": DATETIME_FILTERS,
            "latest_observation": DATETIME_FILTERS,
            "timespan": NUMERIC_FILTERS,
            "number_of_observations": NUMERIC_FILTERS,
            "total_integration_hours": NUMERIC_FILTERS,
            "last_integration_minutes": NUMERIC_FILTERS,
            "all_bands": ["exact"],
            "last_sn": NUMERIC_FILTERS,
            "highest_sn": NUMERIC_FILTERS,
            "lowest_sn": NUMERIC_FILTERS,
            "avg_sn_pipe": NUMERIC_FILTERS,
            "max_sn_pipe": NUMERIC_FILTERS,
            "most_common_project": ["exact"],
            "all_projects": ["exact"],
        }

        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class FoldPulsarSummaryConnection(relay.Connection):
    class Meta:
        node = FoldPulsarSummaryNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Int()
    total_project_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum(
            edge.node.number_of_observations
            for edge in self.edges
            if edge.node.number_of_observations
        )

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum(edge.node.total_integration_hours for edge in self.edges), 1)

    def resolve_total_project_time(self, instance):
        # Too slow n(2)
        total_seconds = sum(
            obs.duration
            for obs in Observation.objects.filter(
                project__short=self.edges[0].node.most_common_project
            )
        )
        return int(total_seconds / 60 / 60)

class PipelineRunNode(DjangoObjectType):
    class Meta:
        model = PipelineRun
        fields = "__all__"
        filter_fields = {
            "id": ["exact"],
            "observation__id": ["exact"],
            "ephemeris__id": ["exact"],
            "template__id": ["exact"],
            "pipeline_name": ["exact"],
            "pipeline_description": ["exact"],
            "pipeline_version": ["exact"],
            "created_at": DATETIME_FILTERS,
            "job_state": ["exact"],
            "location": ["exact"],
            "dm": NUMERIC_FILTERS,
            "dm_err": NUMERIC_FILTERS,
            "dm_epoch": NUMERIC_FILTERS,
            "dm_chi2r": NUMERIC_FILTERS,
            "dm_tres": NUMERIC_FILTERS,
            "sn": NUMERIC_FILTERS,
            "flux": NUMERIC_FILTERS,
            "rm": NUMERIC_FILTERS,
            "percent_rfi_zapped": NUMERIC_FILTERS,
        }

        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class FoldPulsarResultNode(DjangoObjectType):
    class Meta:
        model = FoldPulsarResult
        fields = "__all__"
        filter_fields = {
            # "id": ["exact"],
            "observation__id": ["exact"],
            "pipeline_run__id": ["exact"],
            "pulsar__id": ["exact"],
            "embargo_end_date": DATETIME_FILTERS,
        }
        interfaces = (relay.Node,)
    observation = graphene.Field(ObservationNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class FoldPulsarResultConnection(relay.Connection):
    class Meta:
        node = FoldPulsarResultNode

    total_observations = graphene.Int()
    total_observation_hours = graphene.Int()
    total_estimated_disk_space = graphene.String()
    total_projects = graphene.Int()
    total_timespan_days = graphene.Int()
    max_plot_length = graphene.Int()
    min_plot_length = graphene.Int()
    description = graphene.String()
    ephemeris_link = graphene.String()
    toas_link = graphene.String()

    def resolve_toas_link(self, instance):
        return (
            self.iterable.first()
            .pipeline_run.toas_download_link
        )

    def resolve_ephemeris_link(self, instance):
        return (
            self.iterable.first()
            .pipeline_run.ephemeris_download_link
        )

    def resolve_description(self, instance):
        return self.iterable.first().pulsar.comment

    def resolve_total_observations(self, instance):
        return len(self.edges)

    def resolve_total_observation_hours(self, instance):
        return sum(float(result.observation.duration) for result in self.iterable) / 3600

    def resolve_total_projects(self, instance):
        return len({result.observation.project for result in self.iterable})

    def resolve_total_timespan_days(self, instance):
        if self.iterable:
            max_utc = max(result.observation.utc_start for result in self.iterable)
            min_utc = min(result.observation.utc_start for result in self.iterable)
            duration = max_utc - min_utc
            # Add 1 day to the end result because the timespan should show the rounded up number of days
            return duration.days + 1
        else:
            return 0

    def resolve_total_estimated_disk_space(self, instance):
        estimated_sizes = []
        for results in self.iterable:
            try:
                estimated_sizes.append(
                    math.ceil(results.observation.duration / float(results.observation.fold_tsubint))
                    * results.observation.fold_nbin
                    * results.observation.fold_nchan
                    * results.observation.npol
                    * 2
                )
            except ZeroDivisionError:
                estimated_sizes.append(0)

        total_bytes = sum(estimated_sizes)
        return filesizeformat(total_bytes)

    def resolve_max_plot_length(self, instance):
        return FoldPulsarResult.objects.order_by("observation__duration").last().observation.duration

    def resolve_min_plot_length(self, instance):
        return FoldPulsarResult.objects.order_by("-observation__duration").last().observation.duration





class Query(graphene.ObjectType):
    # pulsar = relay.Node.Field(PulsarNode)
    pulsar = graphene.Field(
        PulsarNode,
        name=graphene.String(required=True),
    )
    allPulsars = DjangoFilterConnectionField(PulsarNode, max_limit=10000)

    # observation = relay.Node.Field(ObservationNode)
    # allObservations = DjangoFilterConnectionField(ObservationNode, max_limit=10000)
    observation = relay.ConnectionField(
        ObservationNodeConnection,
        pulsar=graphene.String(),
        telescope=graphene.String(),
    )
    @login_required
    def resolve_observation(self, info, **kwargs):
        return Observation.get_query(**kwargs)

    mainproject = graphene.Field(
        MainProjectNode,
        name=graphene.String(required=True),
    )
    allMainprojects = DjangoFilterConnectionField(MainProjectNode, max_limit=10000)

    # project = graphene.Field(
    #     ProjectNode,
    #     code=graphene.String(required=True),
    # )
    # allProjects = DjangoFilterConnectionField(ProjectNode, max_limit=10000)
    project = relay.ConnectionField(
        ProjectNodeConnection,
        code=graphene.String(),
    )
    @login_required
    def resolve_project(self, info, **kwargs):
        return Project.get_query(**kwargs)

    ephemeris = relay.Node.Field(EphemerisNode)
    allEphemeriss = DjangoFilterConnectionField(EphemerisNode, max_limit=10000)

    pipelinerun = graphene.Field(PipelineRunNode, id=graphene.Int(required=True))
    allPipelineruns = DjangoFilterConnectionField(PipelineRunNode, max_limit=10000)

    fold_pulsar_summary = relay.ConnectionField(
        FoldPulsarSummaryConnection,
        main_project=graphene.String(),
        most_common_project=graphene.String(),
        band=graphene.String(),
    )

    @login_required
    def resolve_fold_pulsar_summary(self, info, **kwargs):
        return FoldPulsarSummary.get_query(**kwargs)


    fold_pulsar_result = relay.ConnectionField(
        FoldPulsarResultConnection,
        pulsar=graphene.String(),
        mainProject=graphene.String(),
    )

    @login_required
    def resolve_fold_pulsar_result(self, info, **kwargs):
        queryset = FoldPulsarResult.objects.all()

        pulsar_name = kwargs.get('pulsar')
        if pulsar_name:
            queryset = queryset.filter(pulsar__name=pulsar_name)

        main_project_name = kwargs.get('mainProject')
        if main_project_name:
            queryset = queryset.filter(observation__project__main_project__name__iexact=main_project_name)

        return queryset


