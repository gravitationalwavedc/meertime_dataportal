import math
from datetime import datetime

from django.template.defaultfilters import filesizeformat

import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id
from graphql import GraphQLError

from dataportal.models import (
    Pulsar,
    Telescope,
    MainProject,
    Project,
    Ephemeris,
    Template,
    Calibration,
    Observation,
    PipelineRun,
    PulsarFoldResult,
    PulsarFoldSummary,
    PipelineImage,
    PipelineFile,
    Toa,
    Residual,
)

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

class PulsarConnection(relay.Connection):
    class Meta:
        node = PulsarNode


class TelescopeNode(DjangoObjectType):
    class Meta:
        model = Telescope
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class TelescopeConnection(relay.Connection):
    class Meta:
        node = TelescopeNode


class MainProjectNode(DjangoObjectType):
    class Meta:
        model = MainProject
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    telescope = graphene.Field(TelescopeNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class MainProjectConnection(relay.Connection):
    class Meta:
        node = MainProjectNode


class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    main_project = graphene.Field(MainProjectNode)

    embargoPeriod = graphene.Int()

    def resolve_embargoPeriod(self, info):
        return self.embargo_period.days

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ProjectConnection(relay.Connection):
    class Meta:
        node = ProjectNode


class EphemerisNode(DjangoObjectType):
    class Meta:
        model = Ephemeris
        fields = "__all__"
        filter_fields = {
            "p0": NUMERIC_FILTERS,
            "dm": NUMERIC_FILTERS,
            "ephemeris_hash": ["exact"],
        }

        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    project = graphene.Field(ProjectNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class EphemerisConnection(relay.Connection):
    class Meta:
        node = EphemerisNode

class TemplateNode(DjangoObjectType):
    class Meta:
        model = Template
        fields = "__all__"
        filter_fields = {
            "band": ["exact"],
            "created_at": DATETIME_FILTERS,
            "template_hash": ["exact"],
        }
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    project = graphene.Field(ProjectNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class TemplateConnection(relay.Connection):
    class Meta:
        node = TemplateNode


class CalibrationNode(DjangoObjectType):
    class Meta:
        model = Calibration
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class CalibrationConnection(relay.Connection):
    class Meta:
        node = CalibrationNode


class ObservationNode(DjangoObjectType):
    class Meta:
        model = Observation
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    telescope = graphene.Field(TelescopeNode)
    project = graphene.Field(ProjectNode)
    calibration = graphene.Field(CalibrationNode)
    ephemeris = graphene.Field(EphemerisNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ObservationConnection(relay.Connection):
    class Meta:
        node = ObservationNode


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

    # ForeignKey fields
    project = graphene.Field(ProjectNode)
    ephemeris = graphene.Field(EphemerisNode)
    template = graphene.Field(TemplateNode)
    observation = graphene.Field(ObservationNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class PipelineRunConnection(relay.Connection):
    class Meta:
        node = PipelineRunNode

class PipelineImageType(DjangoObjectType):
    class Meta:
        model = PipelineImage
        fields = "__all__"

class PulsarFoldResultNode(DjangoObjectType):
    class Meta:
        model = PulsarFoldResult
        fields = "__all__"
        filter_fields =  "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    observation = graphene.Field(ObservationNode)
    pipeline_run = graphene.Field(PipelineRunNode)
    project = graphene.Field(ProjectNode)

    # # List all the images for this result
    # images = graphene.List(PipelineImageType)

    # @staticmethod
    # def resolve_images(self, instance):
    #     return PipelineImage.objects.filter(pulsar_fold_result=instance)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class PulsarFoldResultConnection(relay.Connection):
    class Meta:
        node = PulsarFoldResultNode

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
        return PulsarFoldResult.objects.order_by("observation__duration").last().observation.duration

    def resolve_min_plot_length(self, instance):
        return PulsarFoldResult.objects.order_by("-observation__duration").last().observation.duration


class PulsarFoldSummaryNode(DjangoObjectType):
    class Meta:
        model = PulsarFoldSummary
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    main_project = graphene.Field(MainProjectNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class PulsarFoldSummaryConnection(relay.Connection):
    class Meta:
        node = PulsarFoldSummaryNode

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


class PipelineImageNode(DjangoObjectType):
    class Meta:
        model = PipelineImage
        fields = "__all__"
        # filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar_fold_result = graphene.Field(PulsarFoldResultNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class PipelineImageConnection(relay.Connection):
    class Meta:
        node = PipelineImageNode


class PipelineFileNode(DjangoObjectType):
    class Meta:
        model = PipelineFile
        fields = "__all__"
        # filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pipeline_run = graphene.Field(PipelineRunNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class PipelineFileConnection(relay.Connection):
    class Meta:
        node = PipelineFileNode


class ToaNode(DjangoObjectType):
    class Meta:
        model = Toa
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pipeline_run = graphene.Field(PipelineRunNode)
    ephemeris = graphene.Field(EphemerisNode)
    template = graphene.Field(TemplateNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ToaConnection(relay.Connection):
    class Meta:
        node = ToaNode


class ResidualNode(DjangoObjectType):
    class Meta:
        model = Residual
        fields = "__all__"
        # filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pipeline_run = graphene.Field(PipelineRunNode)
    ephemeris = graphene.Field(EphemerisNode)
    template = graphene.Field(TemplateNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ResidualConnection(relay.Connection):
    class Meta:
        node = ResidualNode




class Query(graphene.ObjectType):
    pulsar = relay.ConnectionField(
        PulsarConnection,
        name=graphene.String(),
    )
    @login_required
    def resolve_pulsar(self, info, **kwargs):
        return Pulsar.get_query(**kwargs)


    telescope = relay.ConnectionField(
        TelescopeConnection,
    )
    @login_required
    def resolve_telescope(self, info, **kwargs):
        return Telescope.get_query(**kwargs)


    main_project = relay.ConnectionField(
        MainProjectConnection,
        name=graphene.String(required=True),
    )
    @login_required
    def resolve_main_project(self, info, **kwargs):
        return MainProject.get_query(**kwargs)


    project = relay.ConnectionField(
        ProjectConnection,
        code=graphene.String(),
    )
    @login_required
    def resolve_project(self, info, **kwargs):
        return Project.get_query(**kwargs)


    ephemeris = relay.ConnectionField(
        EphemerisConnection,
    )
    @login_required
    def resolve_ephemeris(self, info, **kwargs):
        return Ephemeris.get_query(**kwargs)


    template = relay.ConnectionField(
        TemplateConnection,
    )
    @login_required
    def resolve_template(self, info, **kwargs):
        return Template.get_query(**kwargs)


    calibration = relay.ConnectionField(
        CalibrationConnection,
    )
    @login_required
    def resolve_calibration(self, info, **kwargs):
        return Calibration.get_query(**kwargs)


    observation = relay.ConnectionField(
        ObservationConnection,
        pulsar__name=graphene.String(),
        telescope__name=graphene.String(),
        project__id=graphene.Int(),
        project__short=graphene.String(),
    )
    @login_required
    def resolve_observation(self, info, **kwargs):
        return Observation.get_query(**kwargs)


    pipeline_run = relay.ConnectionField(
        PipelineRunConnection,
        id=graphene.Int(),
    )
    @login_required
    def resolve_pipeline_run(self, info, **kwargs):
        queryset = PipelineRun.objects.all()

        pipeline_run_id = kwargs.get('id')
        if pipeline_run_id:
            queryset = queryset.filter(id=pipeline_run_id)

        return queryset


    pulsar_fold_result = relay.ConnectionField(
        PulsarFoldResultConnection,
        pulsar=graphene.String(),
        mainProject=graphene.String(),
        utcStart=graphene.String(),
        beam=graphene.Int(),
    )
    @login_required
    def resolve_pulsar_fold_result(self, info, **kwargs):
        queryset = PulsarFoldResult.objects.all()

        pulsar_name = kwargs.get('pulsar')
        if pulsar_name:
            queryset = queryset.filter(pulsar__name=pulsar_name)

        main_project_name = kwargs.get('mainProject')
        if main_project_name:
            queryset = queryset.filter(observation__project__main_project__name__iexact=main_project_name)

        utc_start = kwargs.get('utcStart')
        if utc_start:
            queryset = queryset.filter(observation__utc_start=datetime.strptime(utc_start, "%Y-%m-%d-%H:%M:%S"))

        beam = kwargs.get('beam')
        if beam:
            queryset = queryset.filter(observation__beam=beam)

        return queryset
        # return PulsarFoldResult.get_query(**kwargs)


    pulsar_fold_summary = relay.ConnectionField(
        PulsarFoldSummaryConnection,
        main_project=graphene.String(),
        most_common_project=graphene.String(),
        band=graphene.String(),
    )
    @login_required
    def resolve_pulsar_fold_summary(self, info, **kwargs):
        return PulsarFoldSummary.get_query(**kwargs)


    pipeline_image = relay.ConnectionField(
        PipelineImageConnection,
    )
    @login_required
    def resolve_pipeline_image(self, info, **kwargs):
        # return PipelineImage.get_query(**kwargs)
        return PipelineImage.objects.all()


    pipeline_file = relay.ConnectionField(
        PipelineFileConnection,
    )
    @login_required
    def resolve_pipeline_file(self, info, **kwargs):
        return PipelineFile.get_query(**kwargs)


    toa = relay.ConnectionField(
        ToaConnection,
        pulsar=graphene.String(),
        dmcorrected=graphene.Boolean(),
    )
    @login_required
    def resolve_toa(self, info, **kwargs):
        queryset = Toa.objects.all()

        pulsar_name = kwargs.get('pulsar')
        if pulsar_name:
            queryset = queryset.filter(pipeline_run__observation__pulsar__name=pulsar_name)

        dmcorrected = kwargs.get('dmcorrected')
        if dmcorrected:
            queryset = queryset.filter(dm_corrected=dmcorrected)

        return queryset


    residual = relay.ConnectionField(
        ResidualConnection,
    )
    @login_required
    def resolve_residual(self, info, **kwargs):
        return Residual.get_query(**kwargs)