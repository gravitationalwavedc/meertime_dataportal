import math
from datetime import datetime
from collections import Counter

import graphene
import pytz
from django.db.models import Subquery
from django.template.defaultfilters import filesizeformat
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from dataportal.models import (
    Badge,
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    ObservationSummary,
    PipelineFile,
    PipelineImage,
    PipelineRun,
    Project,
    Pulsar,
    PulsarFoldResult,
    PulsarFoldSummary,
    PulsarSearchSummary,
    Telescope,
    Template,
    Toa,
)
from utils import constants

DATETIME_FILTERS = ["exact", "isnull", "lt", "lte", "gt", "gte", "month", "year", "date"]
NUMERIC_FILTERS = ["exact", "lt", "lte", "gt", "gte"]


class Queries:
    pass


class PulsarNode(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = [
            "name",
            "comment",
        ]
        filter_fields = {
            "name": ["exact"],
            "comment": ["exact"],
        }
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
        fields = [
            "name",
        ]
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
        fields = [
            "telescope",
            "name",
        ]
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
        fields = [
            "main_project",
            "code",
            "short",
            "embargo_period",
            "description",
        ]
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
        fields = [
            "pulsar",
            "project",
            "created_at",
            "created_by",
            "ephemeris_data",
            "ephemeris_hash",
            "p0",
            "dm",
            "valid_from",
            "valid_to",
            "comment",
        ]
        filter_fields = {
            "p0": NUMERIC_FILTERS,
            "dm": NUMERIC_FILTERS,
            "ephemeris_hash": ["exact"],
        }

        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    project = graphene.Field(ProjectNode)

    id_int = graphene.Int()

    def resolve_id_int(self, info):
        return self.id

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
        fields = [
            "pulsar",
            "project",
            "template_file",
            "template_hash",
            "band",
            "created_at",
            "created_by",
        ]
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
        fields = [
            "schedule_block_id",
            "calibration_type",
            "location",
            "start",
            "end",
            "all_projects",
            "n_observations",
            "n_ant_min",
            "n_ant_max",
            "total_integration_time_seconds",
            "observations",
        ]
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    id_int = graphene.Int()

    def resolve_id_int(self, info):
        return self.id

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class CalibrationConnection(relay.Connection):
    class Meta:
        node = CalibrationNode


class BadgeNode(DjangoObjectType):
    class Meta:
        model = Badge
        fields = ["name", "description"]
        interfaces = (relay.Node,)


class BadgeConnection(relay.Connection):
    class Meta:
        node = BadgeNode


class ObservationNode(DjangoObjectType):
    class Meta:
        model = Observation
        fields = [
            "pulsar",
            "telescope",
            "project",
            "calibration",
            "embargo_end_date",
            "band",
            "frequency",
            "bandwidth",
            "nchan",
            "beam",
            "nant",
            "nant_eff",
            "npol",
            "obs_type",
            "utc_start",
            "day_of_year",
            "binary_orbital_phase",
            "raj",
            "decj",
            "duration",
            "nbit",
            "tsamp",
            "ephemeris",
            "fold_nbin",
            "fold_nchan",
            "fold_tsubint",
            "filterbank_nbit",
            "filterbank_npol",
            "filterbank_nchan",
            "filterbank_tsamp",
            "filterbank_dm",
            "pulsar_fold_results",
            "toas",
            "badges",
        ]
        filter_fields = {
            "utc_start": DATETIME_FILTERS,
            "duration": NUMERIC_FILTERS,
            "telescope__id": ["exact"],
            "telescope__name": ["exact"],
            "pulsar__id": ["exact"],
            "pulsar__name": ["exact"],
            "project__id": ["exact"],
            "project__short": ["exact"],
        }
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    telescope = graphene.Field(TelescopeNode)
    project = graphene.Field(ProjectNode)
    calibration = graphene.Field(CalibrationNode)
    ephemeris = graphene.Field(EphemerisNode)
    restricted = graphene.Boolean()
    mode_duration = graphene.Int()

    def resolve_restricted(self, info):
        # by default, we assume that the user is restricted
        try:
            # checking whether the user is restricted or not
            user_restricted = info.context.user.role.casefold() == constants.UserRole.RESTRICTED.value.casefold()

            if user_restricted:
                # if the user is restricted, then we check this Pulsar's embargo date
                return self.embargo_end_date >= datetime.now(tz=pytz.UTC)
            else:
                # if the user is not restricted, we return False (restricted)
                return False
        except Exception:
            # default fallback to restricted (True)
            return True

    def resolve_mode_duration(self, instance):
        obs = Observation.objects.all()
        # Filter by input queries
        if "pulsar_Name" in instance.variable_values.keys():
            obs = obs.filter(pulsar__name__in=instance.variable_values["pulsar_Name"])
        if "telescope_Name" in instance.variable_values.keys():
            obs = obs.filter(telescope__name=instance.variable_values["telescope_Name"])
        if "mainProject" in instance.variable_values.keys():
            obs = obs.filter(project__main_project__name__iexact=instance.variable_values["mainProject"])
        if "project_Id" in instance.variable_values.keys():
            obs = obs.filter(project__id=instance.variable_values["project_Id"])
        if "projectShort" in instance.variable_values.keys():
            obs = obs.filter(project_short=instance.variable_values["projectShort"])
        if "obsType" in instance.variable_values.keys():
            obs = obs.filter(obs_type=instance.variable_values["obsType"])
        # Then get the mode of the duration (highest count)
        durations = obs.values('duration')
        # Round to nearest 32 seconds
        rounded_duration = [int(round(duration["duration"] / 32) * 32) for duration in durations]
        counter = Counter(rounded_duration)
        duration_count_pairs = [(value, count) for value, count in counter.items()]
        # Sort by count and then by value to get shortest duration on draws
        duration_count_pairs = sorted(duration_count_pairs, key=lambda x: (-x[1], x[0]))
        return duration_count_pairs[0][0]

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class ObservationConnection(relay.Connection):
    class Meta:
        node = ObservationNode

    pulsar__name = graphene.List(graphene.String)
    telescope__name = graphene.String()
    project__id = graphene.Int()
    project__short = graphene.String()
    utcStart_gte = graphene.DateTime()
    utcStart_lte = graphene.DateTime()

    total_observations = graphene.Int()
    total_observation_hours = graphene.Int()
    total_pulsars = graphene.Int()
    total_observations_tel_lt_35 = graphene.Int()

    def resolve_total_observations(self, instance):
        return len(self.edges)

    def resolve_total_observation_hours(self, instance):
        return sum(float(result.duration) for result in self.iterable) / 3600

    def resolve_total_pulsars(self, instance):
        return len(list(set(result.pulsar.name for result in self.iterable)))

    def resolve_total_observations_tel_lt_35(self, instance):
        n_obs = 0
        for obs in self.iterable:
            if obs.nant < 35:
                n_obs += 1
        return n_obs


class ObservationSummaryNode(DjangoObjectType):
    class Meta:
        model = ObservationSummary
        fields = [
            "pulsar",
            "main_project",
            "project",
            "calibration",
            "obs_type",
            "band",
            "observations",
            "pulsars",
            "projects",
            "estimated_disk_space_gb",
            "observation_hours",
            "timespan_days",
            "min_duration",
            "max_duration",
        ]
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    main_project = graphene.Field(MainProjectNode)
    project = graphene.Field(ProjectNode)
    calibration = graphene.Field(CalibrationNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class ObservationSummaryConnection(relay.Connection):
    class Meta:
        node = ObservationSummaryNode


class PipelineRunNode(DjangoObjectType):
    class Meta:
        model = PipelineRun
        fields = [
            "observation",
            "ephemeris",
            "template",
            "pipeline_name",
            "pipeline_description",
            "pipeline_version",
            "created_at",
            "created_by",
            "job_state",
            "location",
            "configuration",
            "toas_download_link",
            "dm",
            "dm_err",
            "dm_epoch",
            "dm_chi2r",
            "dm_tres",
            "sn",
            "flux",
            "rm",
            "rm_err",
            "percent_rfi_zapped",
            "badges",
        ]
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


class PulsarFoldResultNode(DjangoObjectType):
    class Meta:
        model = PulsarFoldResult
        fields = [
            "observation",
            "pipeline_run",
            "pulsar",
            "images",
        ]
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    observation = graphene.Field(ObservationNode)
    pipeline_run = graphene.Field(PipelineRunNode)
    project = graphene.Field(ProjectNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

    def resolve_images(self, info):
        """
        Check if user is allowed to access the images.
        """
        if self.observation.is_restricted(info.context.user):
            return []

        return self.images.all()


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
    residual_ephemeris = graphene.Field(EphemerisNode)
    toas_link = graphene.String()
    all_projects = graphene.List(graphene.String)
    all_nchans = graphene.List(graphene.Int)
    total_badge_excluded_observations = graphene.Int()

    def resolve_all_projects(self, instance):
        if "pulsar" in instance.variable_values.keys():
            return list(
                Toa.objects.filter(observation__pulsar__name=instance.variable_values["pulsar"])
                .values_list("project__short", flat=True)
                .distinct()
            )
        else:
            return []

    def resolve_all_nchans(self, instance):
        if "pulsar" in instance.variable_values.keys():
            return list(
                Toa.objects.filter(observation__pulsar__name=instance.variable_values["pulsar"])
                .values_list("obs_nchan", flat=True)
                .distinct()
            )
        else:
            return []

    def resolve_toas_link(self, instance):
        return self.iterable.first().pipeline_run.toas_download_link

    def resolve_residual_ephemeris(self, instance):
        pulsar_fold_result = self.iterable.first()
        toas = Toa.objects.select_related("pipeline_run").filter(pipeline_run=pulsar_fold_result.pipeline_run)
        if len(toas) > 0:
            return toas.first().ephemeris
        else:
            return None

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

    def resolve_total_badge_excluded_observations(self, instance):
        if "excludeBadges" in instance.variable_values.keys():
            # First do all other filters
            queryset = PulsarFoldResult.objects.all()
            if "pulsar" in instance.variable_values.keys():
                queryset = queryset.filter(pulsar__name=instance.variable_values["pulsar"])
            if "mainProject" in instance.variable_values.keys():
                queryset = queryset.filter(
                    observation__project__main_project__name__iexact=instance.variable_values["mainProject"]
                )
            if "utcStart" in instance.variable_values.keys():
                queryset = queryset.filter(observation__utc_start=instance.variable_values["utcStart"])
            if "beam" in instance.variable_values.keys():
                queryset = queryset.filter(observation__pulsar__name=instance.variable_values["beam"])
            # Filter and observations with badges
            return queryset.filter(pipeline_run__badges__name__in=instance.variable_values["excludeBadges"]).count()
        else:
            return 0


class PulsarFoldSummaryNode(DjangoObjectType):
    class Meta:
        model = PulsarFoldSummary
        fields = [
            "pulsar",
            "main_project",
            "first_observation",
            "latest_observation",
            "latest_observation_beam",
            "timespan",
            "number_of_observations",
            "total_integration_hours",
            "last_integration_minutes",
            "all_bands",
            "last_sn",
            "highest_sn",
            "lowest_sn",
            "avg_sn_pipe",
            "max_sn_pipe",
            "most_common_project",
            "all_projects",
        ]
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
        return sum(edge.node.number_of_observations for edge in self.edges if edge.node.number_of_observations)

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum(edge.node.total_integration_hours for edge in self.edges), 1)

    def resolve_total_project_time(self, instance):
        # Too slow n(2)
        total_seconds = sum(
            obs.duration for obs in Observation.objects.filter(project__short=self.edges[0].node.most_common_project)
        )
        return int(total_seconds / 60 / 60)


class PulsarSearchSummaryNode(DjangoObjectType):
    class Meta:
        model = PulsarSearchSummary
        fields = [
            "pulsar",
            "main_project",
            "first_observation",
            "latest_observation",
            "timespan",
            "number_of_observations",
            "total_integration_hours",
            "last_integration_minutes",
            "all_bands",
            "most_common_project",
            "all_projects",
        ]
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    main_project = graphene.Field(MainProjectNode)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class PulsarSearchSummaryConnection(relay.Connection):
    class Meta:
        node = PulsarSearchSummaryNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Int()
    total_project_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum(edge.node.number_of_observations for edge in self.edges if edge.node.number_of_observations)

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum(edge.node.total_integration_hours for edge in self.edges), 1)

    def resolve_total_project_time(self, instance):
        # Too slow n(2)
        total_seconds = sum(
            obs.duration for obs in Observation.objects.filter(project__short=self.edges[0].node.most_common_project)
        )
        return int(total_seconds / 60 / 60)


class PipelineImageNode(DjangoObjectType):
    class Meta:
        model = PipelineImage
        fields = [
            "pulsar_fold_result",
            "image",
            "url",
            "cleaned",
            "image_type",
            "resolution",
        ]
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
        fields = [
            "pulsar_fold_result",
            "file",
            "file_type",
        ]
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar_fold_result = graphene.Field(PulsarFoldResultNode)

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
        fields = [
            "pipeline_run",
            "observation",
            "project",
            "ephemeris",
            "template",
            "archive",
            "freq_MHz",
            "mjd",
            "mjd_err",
            "telescope",
            "fe",
            "be",
            "f",
            "bw",
            "tobs",
            "tmplt",
            "gof",
            "nbin",
            "nch",
            "chan",
            "rcvr",
            "snr",
            "length",
            "subint",
            "dm_corrected",
            "minimum_nsubs",
            "maximum_nsubs",
            "all_nsubs",
            "mode_nsubs",
            "obs_nchan",
            "obs_npol",
            "day_of_year",
            "binary_orbital_phase",
            "residual_sec",
            "residual_sec_err",
            "residual_phase",
            "residual_phase_err",
        ]
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

    all_projects = graphene.List(graphene.String)
    all_nchans = graphene.List(graphene.Int)
    total_badge_excluded_toas = graphene.Int()

    def resolve_all_projects(self, instance):
        if "pulsar" in instance.variable_values.keys():
            toa_project_query = Toa.objects.filter(observation__pulsar__name=instance.variable_values["pulsar"])
            if "mainProject" in instance.variable_values.keys():
                toa_project_query = toa_project_query.filter(
                    project__main_project__name__icontains=instance.variable_values["mainProject"]
                )
            return list(toa_project_query.values_list("project__short", flat=True).distinct())
        else:
            return []

    def resolve_all_nchans(self, instance):
        if "pulsar" in instance.variable_values.keys():
            toa_nchan_query = Toa.objects.filter(observation__pulsar__name=instance.variable_values["pulsar"])
            if "mainProject" in instance.variable_values.keys():
                toa_nchan_query = toa_nchan_query.filter(
                    project__main_project__name__icontains=instance.variable_values["mainProject"]
                )
            return list(toa_nchan_query.values_list("obs_nchan", flat=True).distinct())
        else:
            return []

    def resolve_total_badge_excluded_toas(self, instance):
        if "excludeBadges" in instance.variable_values.keys():
            # First do all other filters
            queryset = Toa.objects.select_related(
                "pipeline_run",
                "ephemeris",
                "template",
                "project",
            ).all()
            if "pipelineRunId" in instance.variable_values.keys():
                queryset = queryset.filter(pipeline_run__id=instance.variable_values["pipelineRunId"])
            if "pulsar" in instance.variable_values.keys():
                queryset = queryset.select_related("observation__pulsar").filter(
                    observation__pulsar__name=instance.variable_values["pulsar"]
                )
            if "mainProject" in instance.variable_values.keys():
                queryset = queryset.select_related("observation__project__main_project").filter(
                    observation__project__main_project__name__iexact=instance.variable_values["mainProject"]
                )
            if "projectShort" in instance.variable_values.keys():
                if instance.variable_values["projectShort"] != "All":
                    queryset = queryset.filter(project__short=instance.variable_values["projectShort"])
            if "dmCorrected" in instance.variable_values.keys():
                queryset = queryset.filter(dm_corrected=bool(instance.variable_values["dmCorrected"]))
            if "minimumNsubs" in instance.variable_values.keys():
                if bool(instance.variable_values["minimumNsubs"]):
                    queryset = queryset.filter(minimum_nsubs=True)
            if "maximumNsubs" in instance.variable_values.keys():
                if bool(instance.variable_values["maximumNsubs"]):
                    queryset = queryset.filter(maximum_nsubs=True)
            if "obsNchan" in instance.variable_values.keys():
                queryset = queryset.filter(obs_nchan=instance.variable_values["obsNchan"])
            if "obsNpol" in instance.variable_values.keys():
                queryset = queryset.filter(obs_npol=instance.variable_values["obsNpol"])
            # Filter and observations with badges
            return queryset.filter(pipeline_run__badges__name__in=instance.variable_values["excludeBadges"]).count()
        else:
            return 0


class Query(graphene.ObjectType):
    pulsar = relay.ConnectionField(
        PulsarConnection,
        name=graphene.String(),
    )

    @login_required
    def resolve_pulsar(self, info, **kwargs):
        queryset = Pulsar.objects.all()

        name = kwargs.get("name")
        if name:
            queryset = queryset.filter(name=name)

        return queryset

    telescope = relay.ConnectionField(
        TelescopeConnection,
    )

    @login_required
    def resolve_telescope(self, info, **kwargs):
        queryset = Telescope.objects.all()

        name = kwargs.get("name")
        if name:
            queryset = queryset.filter(name=name)

        return queryset

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
        id=graphene.Int(),
    )

    @login_required
    def resolve_calibration(self, info, **kwargs):
        queryset = Calibration.objects.all()

        calibration_id = kwargs.get("id")
        if calibration_id:
            if calibration_id == -1:
                queryset = [queryset.order_by("start").last()]
            else:
                queryset = queryset.filter(id=calibration_id)

        return queryset

    observation = relay.ConnectionField(
        ObservationConnection,
        pulsar__name=graphene.List(graphene.String),
        telescope__name=graphene.String(),
        main_project=graphene.String(),
        project__id=graphene.Int(),
        project__short=graphene.String(),
        utcStart_gte=graphene.String(),
        utcStart_lte=graphene.String(),
        obs_type=graphene.String(),
        unprocessed=graphene.Boolean(),
        incomplete=graphene.Boolean(),
    )

    @login_required
    def resolve_observation(self, info, **kwargs):
        queryset = Observation.objects.select_related(
            "pulsar", "telescope", "project__main_project", "calibration"
        ).all()

        pulsar_name = kwargs.get("pulsar__name")
        if pulsar_name:
            queryset = queryset.filter(pulsar__name__in=pulsar_name)

        telescope_name = kwargs.get("telescope__name")
        if telescope_name:
            queryset = queryset.filter(telescope__name=telescope_name)

        main_project = kwargs.get("main_project")
        if main_project:
            if main_project != "All":
                queryset = queryset.filter(project__main_project__name__iexact=main_project)

        project_id = kwargs.get("project__id")
        if project_id:
            queryset = queryset.filter(project__id=project_id)

        project_short = kwargs.get("project__short")
        if project_short:
            queryset = queryset.filter(project__short=project_short)

        utcStart_gte = kwargs.get("utcStart_gte")
        if utcStart_gte:
            queryset = queryset.filter(utc_start__gte=utcStart_gte)

        utcStart_lte = kwargs.get("utcStart_lte")
        if utcStart_lte:
            queryset = queryset.filter(utc_start__lte=utcStart_lte)

        obs_type = kwargs.get("obs_type")
        if obs_type:
            queryset = queryset.filter(obs_type=obs_type)

        unprocessed = kwargs.get("unprocessed")
        if unprocessed:
            # Find all observations that have not been processed by finding observations
            # that don't have PulsarFoldResults
            observations_with_fold_results = PulsarFoldResult.objects.values("observation")
            queryset = queryset.exclude(id__in=Subquery(observations_with_fold_results))

        incomplete = kwargs.get("incomplete")
        if incomplete:
            # Find all observations that do not have "Completed" as their most recent job state
            observations_failed = PulsarFoldResult.objects.exclude(pipeline_run__job_state="Completed")
            queryset = queryset.filter(id__in=Subquery(observations_failed.values("observation__id")))

        return queryset

    observation_summary = relay.ConnectionField(
        ObservationSummaryConnection,
        pulsar__name=graphene.String(),
        main_project=graphene.String(),
        project__id=graphene.Int(),
        project__short=graphene.String(),
        calibration__id=graphene.String(),
        calibration_int=graphene.Int(),
        obs_type=graphene.String(),
        band=graphene.String(),
    )

    @login_required
    def resolve_observation_summary(self, info, **kwargs):
        queryset = ObservationSummary.objects.all()

        pulsar_name = kwargs.get("pulsar__name")
        if pulsar_name:
            if pulsar_name == "All":
                pulsar_name = None
            queryset = queryset.filter(pulsar__name=pulsar_name)

        main_project = kwargs.get("main_project")
        if main_project:
            if main_project == "All":
                main_project = None
            queryset = queryset.filter(main_project__name__iexact=main_project)

        project_id = kwargs.get("project__id")
        if project_id:
            queryset = queryset.filter(project__id=project_id)

        project_short = kwargs.get("project__short")
        if project_short:
            if project_short == "All":
                project_short = None
            queryset = queryset.filter(project__short=project_short)

        calibration__id = kwargs.get("calibration__id")
        if calibration__id:
            if calibration__id == "All":
                calibration__id = None
            else:
                queryset = queryset.filter(calibration__id=calibration__id)

        calibration_int = kwargs.get("calibration_int")
        if calibration_int:
            if calibration_int == -1:
                last_cal_id = Calibration.objects.all().order_by("start").last().id
                queryset = queryset.filter(calibration__id=last_cal_id)
            else:
                queryset = queryset.filter(calibration__id=calibration_int)

        obs_type = kwargs.get("obs_type")
        if obs_type:
            if obs_type == "All":
                obs_type = None
            queryset = queryset.filter(obs_type=obs_type)

        band = kwargs.get("band")
        if band:
            if band == "All":
                band = None
            queryset = queryset.filter(band=band)

        return queryset

    pipeline_run = relay.ConnectionField(
        PipelineRunConnection,
        id=graphene.Int(),
    )

    @login_required
    def resolve_pipeline_run(self, info, **kwargs):
        queryset = PipelineRun.objects.all()

        pipeline_run_id = kwargs.get("id")
        if pipeline_run_id:
            queryset = queryset.filter(id=pipeline_run_id)

        return queryset

    pulsar_fold_result = relay.ConnectionField(
        PulsarFoldResultConnection,
        pulsar=graphene.String(),
        mainProject=graphene.String(),
        utcStart=graphene.String(),
        beam=graphene.Int(),
        excludeBadges=graphene.List(graphene.String),
    )

    @login_required
    def resolve_pulsar_fold_result(self, info, **kwargs):
        queryset = PulsarFoldResult.objects.select_related(
            "observation__project",
            "observation__ephemeris",
            "observation__calibration",
            "pipeline_run",
        ).all()

        pulsar_name = kwargs.get("pulsar")
        if pulsar_name:
            queryset = queryset.filter(pulsar__name=pulsar_name)

        main_project_name = kwargs.get("mainProject")
        if main_project_name:
            queryset = queryset.filter(observation__project__main_project__name__iexact=main_project_name)

        utc_start = kwargs.get("utcStart")
        if utc_start:
            queryset = queryset.filter(observation__utc_start=datetime.strptime(utc_start, "%Y-%m-%d-%H:%M:%S"))

        beam = kwargs.get("beam")
        if beam:
            queryset = queryset.filter(observation__beam=beam)

        exclude_badges = kwargs.get("excludeBadges")
        if exclude_badges:
            queryset = queryset.exclude(pipeline_run__badges__name__in=exclude_badges)

        return queryset

    pulsar_fold_summary = relay.ConnectionField(
        PulsarFoldSummaryConnection,
        main_project=graphene.String(),
        most_common_project=graphene.String(),
        project=graphene.String(),
        band=graphene.String(),
    )

    @login_required
    def resolve_pulsar_fold_summary(self, info, **kwargs):
        return PulsarFoldSummary.get_query(**kwargs)

    pulsar_search_summary = relay.ConnectionField(
        PulsarSearchSummaryConnection,
        main_project=graphene.String(),
        most_common_project=graphene.String(),
        project=graphene.String(),
        band=graphene.String(),
    )

    @login_required
    def resolve_pulsar_search_summary(self, info, **kwargs):
        return PulsarSearchSummary.get_query(**kwargs)

    pipeline_image = relay.ConnectionField(
        PipelineImageConnection,
    )

    @login_required
    def resolve_pipeline_image(self, info, **kwargs):
        queryset = PipelineImage.objects.all()

        return queryset

    pipeline_file = relay.ConnectionField(
        PipelineFileConnection,
    )

    @login_required
    def resolve_pipeline_file(self, info, **kwargs):
        queryset = PipelineFile.objects.all()

        return queryset

    toa = relay.ConnectionField(
        ToaConnection,
        pipelineRunId=graphene.Int(),
        pulsar=graphene.String(),
        mainProject=graphene.String(),
        projectShort=graphene.String(),
        dmCorrected=graphene.Boolean(),
        minimumNsubs=graphene.Boolean(),
        maximumNsubs=graphene.Boolean(),
        allNsubs=graphene.Boolean(),
        modeNsubs=graphene.Boolean(),
        obsNchan=graphene.Int(),
        obsNpol=graphene.Int(),
        excludeBadges=graphene.List(graphene.String),
    )

    @login_required
    def resolve_toa(self, info, **kwargs):
        queryset = Toa.objects.select_related(
            "pipeline_run",
            "ephemeris",
            "template",
            "project",
        ).all()

        pipelineRunId = kwargs.get("pipelineRunId")
        if pipelineRunId:
            queryset = queryset.select_related("pipeline_run").filter(pipeline_run__id=pipelineRunId)

        pulsar_name = kwargs.get("pulsar")
        if pulsar_name:
            queryset = queryset.select_related("observation__pulsar").filter(observation__pulsar__name=pulsar_name)

        main_project_name = kwargs.get("mainProject")
        if main_project_name:
            queryset = queryset.select_related("observation__project__main_project").filter(
                observation__project__main_project__name__iexact=main_project_name
            )

        project_short = kwargs.get("projectShort")
        if project_short:
            if project_short != "All":
                queryset = queryset.select_related("project").filter(project__short=project_short)

        dm_corrected = kwargs.get("dmCorrected")
        if dm_corrected is not None:
            queryset = queryset.filter(dm_corrected=bool(dm_corrected))

        # Only filter on True because minimum_nsubs and maximum_nsubs are
        # not mutually exclusive. When the filters are minimum_nsubs=True and
        # maximum_nsubs=False, we want to return all observations that have
        # minimum_nsubs=True regardless of the maximum_nsubs value.
        minimum_nsubs = kwargs.get("minimumNsubs")
        if bool(minimum_nsubs):
            queryset = queryset.filter(minimum_nsubs=True)
        maximum_nsubs = kwargs.get("maximumNsubs")
        if bool(maximum_nsubs):
            queryset = queryset.filter(maximum_nsubs=True)
        all_nsubs = kwargs.get("allNsubs")
        if bool(all_nsubs):
            queryset = queryset.filter(all_nsubs=True)
        mode_nsubs = kwargs.get("modeNsubs")
        if bool(mode_nsubs):
            queryset = queryset.filter(mode_nsubs=True)

        obs_nchan = kwargs.get("obsNchan")
        if obs_nchan:
            queryset = queryset.filter(obs_nchan=obs_nchan)

        obs_npol = kwargs.get("obsNpol")
        if obs_npol:
            queryset = queryset.filter(obs_npol=obs_npol)

        exclude_badges = kwargs.get("excludeBadges")
        if exclude_badges:
            queryset = queryset.exclude(pipeline_run__badges__name__in=exclude_badges)

        return queryset.order_by("mjd")

    badge = relay.ConnectionField(
        BadgeConnection,
    )

    @login_required
    def resolve_badge(self, info, **kwargs):
        return Badge.objects.all()
