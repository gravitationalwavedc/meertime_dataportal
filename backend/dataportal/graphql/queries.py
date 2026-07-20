import math
from collections import Counter
from datetime import datetime
from datetime import timezone as dt_timezone

import django_filters
import graphene
from astropy.time import Time
from django.core.exceptions import ValidationError
from django.db.models import Q, Subquery
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField, TypedFilter
from graphql import GraphQLError

from dataportal.file_utils import get_file_list
from dataportal.models import (
    Badge,
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    ObservationSummary,
    PipelineImage,
    PipelineRun,
    Project,
    ProjectMembership,
    Pulsar,
    PulsarFoldResult,
    PulsarFoldSummary,
    PulsarSearchSummary,
    Telescope,
    Template,
    Toa,
)
from user_manage.graphql.decorators import login_required, user_passes_test

####################################
# Constants for shared filter fields

DATETIME_FILTERS = [
    "exact",
    "isnull",
    "lt",
    "lte",
    "gt",
    "gte",
    "month",
    "year",
    "date",
]
NUMERIC_FILTERS = ["exact", "lt", "lte", "gt", "gte"]


def _observation_is_accessible(observation, request):
    if hasattr(observation, "_is_accessible"):
        return observation._is_accessible
    if request.user.is_superuser:
        return True

    request_now = getattr(request, "_dataportal_access_check_now", None)
    if request_now is None:
        request_now = timezone.now()
        request._dataportal_access_check_now = request_now

    if observation.embargo_end_date is None or observation.embargo_end_date < request_now:
        return True

    # After here we need to ensure no authenticated user can access, so we can skip the database query for
    # unauthenticated users. In short annoymous users can't have project memeberships.
    if not request.user.is_authenticated:
        return False

    membership_project_ids = getattr(request, "_dataportal_membership_project_ids", None)
    membership_user_id = getattr(request, "_dataportal_membership_project_user_id", None)
    current_user_id = request.user.id
    if membership_project_ids is None or membership_user_id != current_user_id:
        membership_project_ids = set(
            ProjectMembership.objects.filter(
                user=request.user,
                is_active=True,
            ).values_list("project_id", flat=True)
        )
        request._dataportal_membership_project_ids = membership_project_ids
        request._dataportal_membership_project_user_id = current_user_id

    return observation.project_id in membership_project_ids


###################################
# File queries

"""
# File actions shouldn't use Django Filter because they aren't connected to a model and we don't want to expose
# filters. These should be the only graphql queries that don't use DjangoFilterConnectionField.
# Don't try to migrate these to DjangoFilerConnectionField, but all other models queries should follow the standard 
# pattern of using DjangoFilterConnectionField and defining filter_fields in the Meta class of the Node
"""


# FileNode and FileConnection classes for file queries
class FileNode(graphene.ObjectType):
    """GraphQL node representing a file or directory"""

    class Meta:
        interfaces = (relay.Node,)

    path = graphene.String(description="Path to the file")
    file_name = graphene.String(description="Name of the file")
    file_size = graphene.String(description="Size of the file in bytes")  # Use string to avoid > 32bit int error
    is_directory = graphene.Boolean(description="Whether this item is a directory")


class FileConnection(relay.Connection):
    """GraphQL connection for files"""

    class Meta:
        node = FileNode


###################################
# Standard model queries.
# These should all use DjanogObjectType and DjangoFilterConnectionField, and define filter_fields in the
# Meta class of the Node


class PulsarNode(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = [
            "name",
            "comment",
        ]
        filter_fields = ["name"]
        interfaces = (relay.Node,)


class TelescopeNode(DjangoObjectType):
    class Meta:
        model = Telescope
        fields = [
            "name",
        ]
        filter_fields = ["name"]
        interfaces = (relay.Node,)


class MainProjectNode(DjangoObjectType):
    class Meta:
        model = MainProject
        fields = [
            "telescope",
            "name",
        ]
        filter_fields = ["telescope__name", "name"]
        interfaces = (relay.Node,)

    # ForeignKey fields
    telescope = graphene.Field(TelescopeNode)


class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        fields = [
            "main_project",
            "code",
            "short",
            "embargo_period",
            "description",
            "is_visible_on_frontend",
            "display_order",
            "band_options",
            "plot_types",
            "allow_downloads",
            "show_extended_observation_fields",
            "observation_band_override",
            "toa_metadata_available",
            "use_for_folding_assets",
        ]
        filter_fields = [
            "main_project__name",
            "code",
            "short",
            "embargo_period",
            "description",
            "display_order",
        ]
        interfaces = (relay.Node,)

    # ForeignKey fields
    main_project = graphene.Field(MainProjectNode)

    embargoPeriod = graphene.Int()
    band_options = graphene.NonNull(graphene.List(graphene.NonNull(graphene.String)))
    plot_types = graphene.NonNull(graphene.List(graphene.NonNull(graphene.String)))

    def resolve_embargoPeriod(self, info):
        return self.embargo_period.days

    def resolve_band_options(self, info):
        return self.band_options

    def resolve_plot_types(self, info):
        return self.plot_types


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
            "pulsar__name": ["exact"],
            "project__short": ["exact"],
        }

        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    project = graphene.Field(ProjectNode)

    id_int = graphene.Int()

    def resolve_id_int(self, info):
        return self.id

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.accessible_to(info.context.user)

    def resolve_project(self, info):
        return self.project


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
            "pulsar__name": ["exact"],
            "project__short": ["exact"],
        }
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    project = graphene.Field(ProjectNode)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.accessible_to(info.context.user)

    def resolve_project(self, info):
        return self.project


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
            "badges",
        ]
        filter_fields = [
            "schedule_block_id",
            "calibration_type",
            "location",
            "start",
            "end",
            "all_projects",
            "n_observations",
            "n_ant_min",
            "n_ant_max",
        ]
        interfaces = (relay.Node,)

    id_int = graphene.Int()

    def resolve_id_int(self, info):
        return self.id


class BadgeNode(DjangoObjectType):
    class Meta:
        model = Badge
        fields = ["name", "description"]
        filter_fields = {
            "name": ["exact", "icontains"],
            "description": ["icontains"],
        }
        interfaces = (relay.Node,)


class ObservationFilterSet(django_filters.FilterSet):
    pulsar__name = TypedFilter(
        input_type=graphene.List(graphene.String),
        field_name="pulsar__name",
        lookup_expr="in",
    )
    telescope__name = django_filters.CharFilter(field_name="telescope__name", lookup_expr="exact")
    main_project = django_filters.CharFilter(method="filter_main_project")
    project__id = TypedFilter(input_type=graphene.Int, field_name="project__id")
    project__short = django_filters.CharFilter(method="filter_project_short")
    utc_start_gte = TypedFilter(
        input_type=graphene.String,
        field_name="utc_start",
        lookup_expr="gte",
    )
    utc_start_lte = TypedFilter(
        input_type=graphene.String,
        field_name="utc_start",
        lookup_expr="lte",
    )
    obs_type = django_filters.CharFilter(method="filter_obs_type")
    unprocessed = django_filters.BooleanFilter(method="filter_unprocessed")
    incomplete = django_filters.BooleanFilter(method="filter_incomplete")

    class Meta:
        model = Observation
        fields = []

    def filter_main_project(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(project__main_project__name__iexact=value)

    def filter_project_short(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(project__short=value)

    def filter_obs_type(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(obs_type=value)

    def filter_unprocessed(self, queryset, name, value):
        if not value:
            return queryset
        observations_with_fold_results = PulsarFoldResult.objects.values("observation")
        return queryset.exclude(id__in=Subquery(observations_with_fold_results))

    def filter_incomplete(self, queryset, name, value):
        if not value:
            return queryset
        observations_failed = PulsarFoldResult.objects.exclude(pipeline_run__job_state="Completed")
        return queryset.filter(id__in=Subquery(observations_failed.values("observation__id")))


class ObservationSummaryFilterSet(django_filters.FilterSet):
    pulsar__name = django_filters.CharFilter(field_name="pulsar__name", lookup_expr="exact")
    pulsar_isnull = django_filters.BooleanFilter(field_name="pulsar", lookup_expr="isnull")
    main_project = django_filters.CharFilter(field_name="main_project__name", lookup_expr="iexact")
    project__id = TypedFilter(input_type=graphene.Int, field_name="project__id")
    project__short = django_filters.CharFilter(field_name="project__short", lookup_expr="exact")
    project_isnull = django_filters.BooleanFilter(field_name="project", lookup_expr="isnull")
    calibration__id = TypedFilter(input_type=graphene.String, field_name="calibration__id")
    calibration_isnull = django_filters.BooleanFilter(field_name="calibration", lookup_expr="isnull")
    calibration_int = TypedFilter(input_type=graphene.Int, field_name="calibration__id")
    obs_type = django_filters.CharFilter(field_name="obs_type", lookup_expr="exact")
    band = django_filters.CharFilter(field_name="band", lookup_expr="exact")
    band_isnull = django_filters.BooleanFilter(field_name="band", lookup_expr="isnull")

    class Meta:
        model = ObservationSummary
        fields = []

    def filter_queryset(self, queryset):
        def has_concrete_value(value):
            # django-filter treats empty string / null-like values as "skip filter".
            # For conflict checks we only care about values that would actively constrain
            # the queryset (for example "PTA", "LBAND", a calibration id).
            if value is None:
                return False
            if isinstance(value, str):
                return value.strip() != ""
            return True

        cleaned_data = self.form.cleaned_data
        # Aggregate summary rows are represented by NULL dimension fields.
        # Exposing *Isnull lets the frontend explicitly request that aggregate grain.
        # Passing both aggregate and concrete filters at once is contradictory, so we
        # fail fast with a clear validation error instead of returning ambiguous results.
        contradictions = (
            (
                "pulsar_isnull",
                "pulsar__name",
                "pulsarIsnull: true",
                "pulsar_Name",
            ),
            (
                "project_isnull",
                "project__short",
                "projectIsnull: true",
                "project_Short",
            ),
            (
                "band_isnull",
                "band",
                "bandIsnull: true",
                "band",
            ),
            (
                "calibration_isnull",
                "calibration__id",
                "calibrationIsnull: true",
                "calibration_Id",
            ),
        )
        for null_key, exact_key, null_arg, exact_arg in contradictions:
            if cleaned_data.get(null_key) is True and has_concrete_value(cleaned_data.get(exact_key)):
                raise ValidationError(f"Cannot combine `{null_arg}` with `{exact_arg}`.")

        return super().filter_queryset(queryset)


class CalibrationFilterSet(django_filters.FilterSet):
    id = TypedFilter(input_type=graphene.Int, field_name="id")

    class Meta:
        model = Calibration
        fields = []


class PulsarFoldResultFilterSet(django_filters.FilterSet):
    pulsar = django_filters.CharFilter(field_name="pulsar__name", lookup_expr="exact")
    main_project = django_filters.CharFilter(
        field_name="observation__project__main_project__name",
        lookup_expr="iexact",
    )
    utc_start = django_filters.CharFilter(method="filter_utc_start")
    beam = TypedFilter(input_type=graphene.Int, field_name="observation__beam")
    exclude_badges = TypedFilter(
        input_type=graphene.List(graphene.String),
        method="filter_exclude_badges",
    )
    # using anything but camelCase for minimum snr results in minimumSnr.
    minimumSNR = TypedFilter(input_type=graphene.Float, field_name="pipeline_run__sn", lookup_expr="gte")
    utc_start_gte = TypedFilter(input_type=graphene.String, field_name="observation__utc_start", lookup_expr="gte")
    utc_start_lte = TypedFilter(input_type=graphene.String, field_name="observation__utc_start", lookup_expr="lte")

    def filter_utc_start(self, queryset, name, value):
        if not value:
            return queryset
        naive_dt = datetime.strptime(value, "%Y-%m-%d-%H:%M:%S")
        aware_dt = naive_dt.replace(tzinfo=dt_timezone.utc)
        return queryset.filter(observation__utc_start=aware_dt)

    def filter_exclude_badges(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.exclude(pipeline_run__badges__name__in=value).exclude(
            pipeline_run__observation__calibration__badges__name__in=value
        )

    class Meta:
        model = PulsarFoldResult
        fields = []


class PulsarFoldSummaryFilterSet(django_filters.FilterSet):
    main_project = django_filters.CharFilter(field_name="main_project__name", lookup_expr="icontains")
    most_common_project = django_filters.CharFilter(field_name="most_common_project", lookup_expr="icontains")
    project = django_filters.CharFilter(field_name="all_projects", lookup_expr="icontains")
    band = django_filters.CharFilter(field_name="all_bands", lookup_expr="icontains")

    class Meta:
        model = PulsarFoldSummary
        fields = []


class PulsarSearchSummaryFilterSet(django_filters.FilterSet):
    main_project = django_filters.CharFilter(field_name="main_project__name", lookup_expr="icontains")
    most_common_project = django_filters.CharFilter(field_name="most_common_project", lookup_expr="icontains")
    project = django_filters.CharFilter(field_name="all_projects", lookup_expr="icontains")
    band = django_filters.CharFilter(field_name="all_bands", lookup_expr="icontains")

    class Meta:
        model = PulsarSearchSummary
        fields = []


class ToaFilterSet(django_filters.FilterSet):
    pipeline_run_id = TypedFilter(input_type=graphene.Int, field_name="pipeline_run__id")
    pulsar = django_filters.CharFilter(field_name="observation__pulsar__name", lookup_expr="exact")
    main_project = django_filters.CharFilter(
        field_name="observation__project__main_project__name",
        lookup_expr="iexact",
    )
    project_short = django_filters.CharFilter(field_name="project__short", lookup_expr="exact")
    dm_corrected = django_filters.BooleanFilter(field_name="dm_corrected")
    nsub_type = django_filters.CharFilter(field_name="nsub_type", lookup_expr="exact")
    obs_nchan = TypedFilter(input_type=graphene.Int, field_name="obs_nchan")
    obs_npol = TypedFilter(input_type=graphene.Int, field_name="obs_npol")
    exclude_badges = TypedFilter(
        input_type=graphene.List(graphene.String),
        method="filter_exclude_badges",
    )
    # using anything but camelCase for minimum snr results in minimumSnr.
    minimumSNR = TypedFilter(input_type=graphene.Float, field_name="snr", lookup_expr="gte")
    utc_start_gte = TypedFilter(input_type=graphene.String, field_name="observation__utc_start", lookup_expr="gte")
    utc_start_lte = TypedFilter(input_type=graphene.String, field_name="observation__utc_start", lookup_expr="lte")

    def filter_exclude_badges(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.exclude(pipeline_run__badges__name__in=value).exclude(
            pipeline_run__observation__calibration__badges__name__in=value
        )

    class Meta:
        model = Toa
        fields = []


class ObservationConnection(relay.Connection):
    class Meta:
        abstract = True

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


class ObservationNode(DjangoObjectType):
    class Meta:
        model = Observation
        connection_class = ObservationConnection
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
    is_embargoed = graphene.Boolean()
    mode_duration = graphene.Int()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.accessible_to(info.context.user)

    def resolve_restricted(self, info):
        return self.is_restricted(info.context.user)

    def resolve_is_embargoed(self, info):
        return self.is_embargoed

    def resolve_project(self, info):
        return self.project

    def resolve_telescope(self, info):
        if not info.context.user.is_authenticated:
            return None
        return self.telescope

    def resolve_ephemeris(self, info):
        if self.ephemeris is None:
            return None
        if hasattr(self, "_ephemeris_is_accessible"):
            return self.ephemeris if self._ephemeris_is_accessible else None
        if self.ephemeris.is_restricted(info.context.user):
            return None
        return self.ephemeris

    def resolve_mode_duration(self, info):
        obs = Observation.objects.accessible_to(info.context.user)
        # Filter by input queries
        # Map GraphQL filter names to Django filter names
        filter_map = {
            "pulsar_Name": "pulsar__name__in",
            "telescope_Name": "telescope__name",
            "mainProject": "project__main_project__name__iexact",
            "project_Id": "project__id",
            "project_Short": "project__short",
            "obsType": "obs_type",
        }

        # Build filters dictionary with only values that exist
        filters = {
            filter_map[key]: value for key, value in info.variable_values.items() if key in filter_map and value
        }

        # Apply all filters at once if any exist
        if filters:
            obs = obs.filter(**filters)
        # Then get the mode of the duration (highest count)
        durations = obs.values("duration")
        # Round to nearest 32 seconds
        rounded_duration = [int(round(duration["duration"] / 32) * 32) for duration in durations]
        counter = Counter(rounded_duration)
        duration_count_pairs = [(value, count) for value, count in counter.items()]
        if not duration_count_pairs:
            return None
        # Sort by count and then by value to get shortest duration on draws
        duration_count_pairs = sorted(duration_count_pairs, key=lambda x: (-x[1], x[0]))
        return duration_count_pairs[0][0]


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
        filter_fields = [
            "pulsar__name",
            "main_project__name",
            "project__id",
            "project__short",
            "calibration__id",
            "obs_type",
            "band",
        ]
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    main_project = graphene.Field(MainProjectNode)
    project = graphene.Field(ProjectNode)
    calibration = graphene.Field(CalibrationNode)


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
    def get_queryset(cls, queryset, info):
        return queryset.accessible_to(info.context.user)

    def resolve_observation(self, info):
        return self.observation

    def resolve_ephemeris(self, info):
        if self.ephemeris is None:
            return None
        if hasattr(self, "_ephemeris_is_accessible"):
            return self.ephemeris if self._ephemeris_is_accessible else None
        if self.ephemeris.is_restricted(info.context.user):
            return None
        return self.ephemeris

    def resolve_template(self, info):
        if self.template is None:
            return None
        if hasattr(self, "_template_is_accessible"):
            return self.template if self._template_is_accessible else None
        if self.template.is_restricted(info.context.user):
            return None
        return self.template

    def resolve_dm_err(self, info):
        """
        Return None for any non-scalar dm_err values (inf, -inf, nan).
        GraphQL Float scalar type cannot represent these values.
        """
        return None if self.dm_err is None or math.isinf(self.dm_err) or math.isnan(self.dm_err) else self.dm_err


class TimingResidualPlotDataType(ObjectType):
    day = graphene.Float()
    size = graphene.Float()
    band = graphene.String()
    error = graphene.Float()
    link = graphene.String()
    phase = graphene.Float()
    snr = graphene.Float()
    utc = graphene.Float()
    value = graphene.Float()


class PulsarFoldResultConnection(relay.Connection):
    """
    Handle the return of multiple observations for a pulsar fold result query, such as on the
    FoldDetail page where we return all observations for a pulsar and then
    determine on the frontend which one to show based on access to ephemeris and template.

    A variable that is set it "" signals that all values should be returned. It used to be "All" but using an empty
    string matches the way django-filters works.
    """

    total_observations = graphene.Int()
    total_observation_hours = graphene.Int()
    total_estimated_disk_space = graphene.String()
    total_projects = graphene.Int()
    total_timespan_days = graphene.Int()
    total_observations = graphene.Int()
    total_toa = graphene.Field(
        graphene.Int,
        pulsar=graphene.String(required=True),
        main_project=graphene.String(default_value="Meertime"),
        project_short=graphene.String(default_value=""),
        nsub_type=graphene.String(default_value="1"),
    )
    max_plot_length = graphene.Int()
    min_plot_length = graphene.Int()
    description = graphene.String()
    folding_ephemeris = graphene.Field(EphemerisNode)
    folding_ephemeris_is_embargoed = graphene.Boolean()
    folding_ephemeris_exists_but_inaccessible = graphene.Boolean()
    folding_template = graphene.Field(TemplateNode)
    folding_template_is_embargoed = graphene.Boolean()
    folding_template_exists_but_inaccessible = graphene.Boolean()

    def _get_fold_access_cache(self):
        cache = getattr(self, "_fold_access_cache", None)
        if cache is None:
            cache = {}
            self._fold_access_cache = cache
        return cache

    def _get_fold_candidate_pfrs(self, instance):
        """
        Build the fold-candidate PFR list from query variables, independent of
        observation access filtering.
        """
        cache = PulsarFoldResultConnection._get_fold_access_cache(self)
        cache_key = "fold_candidate_pfrs"
        if cache_key in cache:
            return cache[cache_key]

        iterable = getattr(self, "iterable", None)
        if iterable is not None:
            queryset = iterable
            if hasattr(queryset, "select_related"):
                queryset = queryset.select_related(
                    "observation__project",
                    "pipeline_run__ephemeris__project",
                    "pipeline_run__template__project",
                    "pipeline_run",
                )
        else:
            queryset = PulsarFoldResult.objects.select_related(
                "observation__project",
                "pipeline_run__ephemeris__project",
                "pipeline_run__template__project",
                "pipeline_run",
            ).all()
            variable_values = getattr(instance, "variable_values", {}) or {}
            pipeline_run_id = variable_values.get("pipelineRunId")
            if pipeline_run_id:
                queryset = queryset.filter(pipeline_run__id=pipeline_run_id)

            pulsar = variable_values.get("pulsar")
            if pulsar:
                queryset = queryset.filter(observation__pulsar__name=pulsar)

            main_project = variable_values.get("mainProject") or variable_values.get("main_project")
            if main_project:
                queryset = queryset.filter(observation__project__main_project__name__iexact=main_project)

            beam = variable_values.get("beam")
            if beam is not None:
                queryset = queryset.filter(observation__beam=beam)

        candidates = list(queryset)
        cache[cache_key] = candidates
        return candidates

    toas_link = graphene.String()
    all_projects = graphene.List(graphene.String)
    most_common_project = graphene.String()
    all_nchans = graphene.List(graphene.Int)
    timing_residual_plot_data = graphene.Field(
        graphene.List(TimingResidualPlotDataType),
        pulsar=graphene.String(required=True),
        main_project=graphene.String(default_value="Meertime"),
        project_short=graphene.String(default_value=""),
        nsub_type=graphene.String(default_value="1"),
        obs_nchan=graphene.Int(default_value=32),
        exclude_badges=graphene.List(graphene.String, default_value=[]),
        minimumSNR=graphene.Float(default_value=8),
        dm_corrected=graphene.Boolean(default_value=False),
    )

    class Meta:
        abstract = True

    def resolve_total_toa(self, instance, **kwargs):
        toas = Toa.objects.accessible_to(instance.context.user).filter(
            observation__pulsar__name=kwargs.get("pulsar"),
            observation__project__main_project__name__iexact=kwargs.get("main_project"),
            dm_corrected=False,
            obs_nchan=32,
            nsub_type=kwargs.get("nsub_type"),
        )

        if kwargs.get("project_short") != "":
            toas = toas.filter(project__short=kwargs.get("project_short"))

        return toas.count()

    def resolve_most_common_project(self, instance):
        first = self.iterable.first() if self.iterable else None
        if first is None:
            return None
        summary = first.pulsar.pulsarfoldsummary_set.first()
        return summary.most_common_project if summary else None

    def resolve_timing_residual_plot_data(self, info, **kwargs):
        toas = (
            Toa.objects.accessible_to(info.context.user)
            .select_related(
                "pipeline_run",
                "observation__pulsar",
                "observation__project__main_project",
                "observation",
            )
            .prefetch_related(
                "pipeline_run__badges",
                "pipeline_run__observation__calibration__badges",
                "observation__badges",
            )
            .filter(
                observation__pulsar__name=kwargs.get("pulsar"),
                observation__project__main_project__name__iexact=kwargs.get("main_project"),
                dm_corrected=kwargs.get("dm_corrected"),
                nsub_type=kwargs.get("nsub_type"),
                obs_nchan=kwargs.get("obs_nchan"),
                snr__gte=kwargs.get("minimumSNR"),
            )
            .exclude(pipeline_run__badges__name__in=kwargs.get("exclude_badges"))
            .exclude(pipeline_run__observation__calibration__badges__name__in=kwargs.get("exclude_badges"))
            .exclude(pipeline_run__observation__badges__name__in=kwargs.get("exclude_badges"))
        )

        if kwargs.get("project_short") != "":
            toas = toas.filter(project__short=kwargs.get("project_short"))

        toas = toas.order_by("mjd").values(
            "observation__band",
            "day_of_year",
            "observation__duration",
            "residual_sec",
            "residual_sec_err",
            "snr",
            "binary_orbital_phase",
            "mjd",
            "observation__utc_start",
            "observation__beam",
        )

        def mjd_to_unix_milliseconds(mjd):
            t = Time(mjd, format="mjd")
            return t.unix

        return [
            {
                "band": t["observation__band"],
                "day": t["day_of_year"],
                "size": t["observation__duration"],
                "error": t["residual_sec_err"],
                "value": t["residual_sec"],
                "snr": t["snr"],
                "phase": t["binary_orbital_phase"],
                "utc": mjd_to_unix_milliseconds(t["mjd"]),
                "link": f"/{kwargs.get('main_project')}/{kwargs.get('pulsar')}/{t['observation__utc_start'].strftime('%Y-%m-%d-%H:%M:%S')}/{t['observation__beam']}/",
            }
            for t in toas
        ]

    def resolve_all_projects(self, instance):
        # print(self.iterable.first().pulsar.pulsar_fold_summary.all_projects)
        if "pulsar" in instance.variable_values.keys():
            return list(
                Toa.objects.accessible_to(instance.context.user)
                .filter(observation__pulsar__name=instance.variable_values["pulsar"])
                .values_list("project__short", flat=True)
                .distinct()
            )
        else:
            return []

    def resolve_all_nchans(self, instance):
        if "pulsar" not in instance.variable_values.keys():
            return []

        values = list(
            Toa.objects.accessible_to(instance.context.user)
            .filter(observation__pulsar__name=instance.variable_values["pulsar"])
            .values_list("obs_nchan", flat=True)
            .order_by("obs_nchan")
            .distinct()
        )
        return sorted(values)

    def resolve_toas_link(self, instance):
        first = self.iterable.first() if self.iterable else None
        if first is None:
            return None
        if not _observation_is_accessible(first.observation, instance.context):
            return None
        return first.pipeline_run.toas_download_link

    def _get_accessible_ephemeris_pfr(self, instance):
        """
        Helper method to find the PulsarFoldResult with the latest accessible ephemeris.

        Returns a tuple of (ephemeris, pfr, valid_pfrs_exist) where:
        - ephemeris: The accessible ephemeris or None
        - pfr: The PulsarFoldResult or None
        - valid_pfrs_exist: Boolean indicating if any valid ephemerides exist (regardless of access)

        IMPORTANT: Embargo is based on EPHEMERIS creation date, not observation or pipeline run dates.

        Logic Flow:
        -----------
        1. Filter valid PulsarFoldResults from self.iterable:
           - Skip if pipeline_run.ephemeris is None
           - Skip if ephemeris.project is not eligible for folding assets
           - Skip if pipeline_run has no TOAs

        2. Sort remaining PulsarFoldResults by pipeline_run.created_at (most recent first)

        3. Bulk-evaluate ephemeris access once via `Ephemeris.objects.accessible_to(user)`.
        4. For each PulsarFoldResult (newest first):
           - If ephemeris id is in accessible set: RETURN (ephemeris, pfr)
           - Otherwise continue
        5. If no accessible ephemeris found: RETURN (None, None)

        Key Points:
        -----------
        - Only one PulsarFoldResult exists for each observation, it is updated with the most recent pipeline run automatically (not here). These are the PFR's that we are iterating on
        - We reorder the PulsarFoldResults (equivalent to observation list with processing results) on the FoldDetail page by which one has had the most recent pipeline run
        - Access policy comes from model-layer `EphemerisQuerySet.accessible_to()`
        - Membership checks are not duplicated in resolver logic
        """
        cache = PulsarFoldResultConnection._get_fold_access_cache(self)
        cache_key = "accessible_ephemeris_pfr_result"
        if cache_key in cache:
            return cache[cache_key]

        user = instance.context.user
        iterable = PulsarFoldResultConnection._get_fold_candidate_pfrs(self, instance)
        pipeline_run_ids = {pfr.pipeline_run_id for pfr in iterable}
        runs_with_toas = set(
            Toa.objects.filter(pipeline_run_id__in=pipeline_run_ids)
            .values_list("pipeline_run_id", flat=True)
            .distinct()
        )

        valid_pfrs = []
        for pfr in iterable:
            # Skip pipeline runs without ephemeris
            if pfr.pipeline_run.ephemeris is None:
                continue
            ephemeris_project = getattr(pfr.pipeline_run.ephemeris, "project", None)
            if ephemeris_project and not ephemeris_project.use_for_folding_assets:
                continue
            # Skip pipeline runs without TOAs
            pipeline_run_id = getattr(pfr, "pipeline_run_id", None) or getattr(pfr.pipeline_run, "id", None)
            if pipeline_run_id not in runs_with_toas:
                continue
            valid_pfrs.append(pfr)

        if not valid_pfrs:
            return None, None, False

        # Sort by pipeline run created_at (most recent first)
        valid_pfrs.sort(key=lambda x: x.pipeline_run.created_at, reverse=True)

        ephemeris_ids = {pfr.pipeline_run.ephemeris_id for pfr in valid_pfrs if pfr.pipeline_run.ephemeris_id}
        accessible_ephemeris_ids = set(
            Ephemeris.objects.accessible_to(user).filter(id__in=ephemeris_ids).values_list("id", flat=True)
        )

        # Find the first pipeline run the user can access
        for pfr in valid_pfrs:
            ephemeris = pfr.pipeline_run.ephemeris
            if ephemeris.id in accessible_ephemeris_ids:
                result = (ephemeris, pfr, True)
                cache[cache_key] = result
                return result

        # No accessible ephemeris found, but valid ephemerides do exist
        result = (None, None, True)
        cache[cache_key] = result
        return result

    def _get_accessible_template_pfr(self, instance):
        """
        Helper method to find the PulsarFoldResult with the latest accessible template.

        Returns a tuple of (template, pfr, valid_pfrs_exist) where:
        - template: The accessible template or None
        - pfr: The PulsarFoldResult or None
        - valid_pfrs_exist: Boolean indicating if any valid templates exist (regardless of access)

        IMPORTANT: Embargo is based on TEMPLATE creation date, not observation or pipeline run dates.

        Logic Flow:
        -----------
        1. Filter valid PulsarFoldResults from self.iterable:
           - Skip if pipeline_run.template is None
           - Skip if template.project is not eligible for folding assets
           - Skip if pipeline_run has no TOAs

        2. Sort remaining PulsarFoldResults by pipeline_run.created_at (most recent first)

        3. Bulk-evaluate template access once via `Template.objects.accessible_to(user)`.
        4. For each PulsarFoldResult (newest first):
           - If template id is in accessible set: RETURN (template, pfr)
           - Otherwise continue
        5. If no accessible template found: RETURN (None, None)

        Key Points:
        -----------
        - Only one PulsarFoldResult exists for each observation, it is updated with the most recent pipeline run automatically
        - We reorder the PulsarFoldResults by which one has had the most recent pipeline run
        - Access policy comes from model-layer `TemplateQuerySet.accessible_to()`
        - Membership checks are not duplicated in resolver logic
        """
        cache = PulsarFoldResultConnection._get_fold_access_cache(self)
        cache_key = "accessible_template_pfr_result"
        if cache_key in cache:
            return cache[cache_key]

        user = instance.context.user
        iterable = PulsarFoldResultConnection._get_fold_candidate_pfrs(self, instance)
        pipeline_run_ids = {pfr.pipeline_run_id for pfr in iterable}
        runs_with_toas = (
            Toa.objects.filter(pipeline_run_id__in=pipeline_run_ids)
            .values_list("pipeline_run_id", flat=True)
            .distinct()
        )

        valid_pfrs = []
        for pfr in iterable:
            # Skip pipeline runs without template
            if pfr.pipeline_run.template is None:
                continue
            template_project = getattr(pfr.pipeline_run.template, "project", None)
            if template_project and not template_project.use_for_folding_assets:
                continue
            # Skip pipeline runs without TOAs
            pipeline_run_id = getattr(pfr, "pipeline_run_id", None) or getattr(pfr.pipeline_run, "id", None)
            if pipeline_run_id not in runs_with_toas:
                continue
            valid_pfrs.append(pfr)

        if not valid_pfrs:
            return None, None, False

        # Sort by pipeline run created_at (most recent first)
        valid_pfrs.sort(key=lambda x: x.pipeline_run.created_at, reverse=True)

        template_ids = {pfr.pipeline_run.template_id for pfr in valid_pfrs if pfr.pipeline_run.template_id}
        accessible_template_ids = set(
            Template.objects.accessible_to(user).filter(id__in=template_ids).values_list("id", flat=True)
        )

        # Find the first pipeline run the user can access
        for pfr in valid_pfrs:
            template = pfr.pipeline_run.template
            if template.id in accessible_template_ids:
                result = (template, pfr, True)
                cache[cache_key] = result
                return result

        # No accessible template found, but valid templates do exist
        result = (None, None, True)
        cache[cache_key] = result
        return result

    def resolve_folding_ephemeris(self, instance):
        """Returns the ephemeris from the latest observation the user has access to."""
        ephemeris, _, _ = self._get_accessible_ephemeris_pfr(instance)
        return ephemeris

    def resolve_folding_ephemeris_is_embargoed(self, instance):
        """
        Returns True if the folding ephemeris is embargoed.

        Note: This checks if the ephemeris is embargoed (based on ephemeris.created_at),
        NOT if the observation or pipeline run is embargoed.

        This helps the frontend display the correct message to users about what
        ephemeris they are viewing:
        - If True: User is viewing embargoed data (they have project membership or are superuser)
        - If False: User is viewing public/non-embargoed data
        - If None: No ephemeris is available
        """
        ephemeris, pfr, _ = self._get_accessible_ephemeris_pfr(instance)
        if ephemeris is None:
            return None

        # Check if the ephemeris is embargoed
        now = timezone.now()
        embargo_end_date = ephemeris.created_at + ephemeris.project.embargo_period
        return embargo_end_date >= now

    def resolve_folding_ephemeris_exists_but_inaccessible(self, instance):
        """
        Returns True if valid ephemerides exist but none are accessible to the user.
        Returns False if no valid ephemerides exist at all.
        Returns None if an accessible ephemeris was found.

        This helps the frontend differentiate between:
        - No ephemerides exist at all (False)
        - Ephemerides exist but are all embargoed/inaccessible (True)
        - An accessible ephemeris is available (None)
        """
        ephemeris, _, valid_pfrs_exist = self._get_accessible_ephemeris_pfr(instance)

        if ephemeris is not None:
            # User has access to an ephemeris
            return None

        # No accessible ephemeris found
        # Return True if valid ephemerides exist (but are inaccessible)
        # Return False if no valid ephemerides exist at all
        return valid_pfrs_exist

    def resolve_folding_template(self, instance):
        """Returns the template from the latest observation the user has access to."""
        template, _, _ = self._get_accessible_template_pfr(instance)
        return template

    def resolve_folding_template_is_embargoed(self, instance):
        """
        Returns True if the folding template is embargoed.

        Note: This checks if the template is embargoed (based on template.created_at),
        NOT if the observation or pipeline run is embargoed.

        This helps the frontend display the correct message to users about what
        template they are viewing:
        - If True: User is viewing embargoed data (they have project membership or are superuser)
        - If False: User is viewing public/non-embargoed data
        - If None: No template is available
        """
        template, pfr, _ = self._get_accessible_template_pfr(instance)
        if template is None:
            return None

        # Check if the template is embargoed
        return template.is_embargoed

    def resolve_folding_template_exists_but_inaccessible(self, instance):
        """
        Returns True if valid templates exist but none are accessible to the user.
        Returns False if no valid templates exist at all.
        Returns None if an accessible template was found.

        This helps the frontend differentiate between:
        - No templates exist at all (False)
        - Templates exist but are all embargoed/inaccessible (True)
        - An accessible template is available (None)
        """
        template, _, valid_pfrs_exist = self._get_accessible_template_pfr(instance)

        if template is not None:
            # User has access to a template
            return None

        # No accessible template found
        # Return True if valid templates exist (but are inaccessible)
        # Return False if no valid templates exist at all
        return valid_pfrs_exist

    def resolve_description(self, instance):
        first = self.iterable.first() if self.iterable else None
        if first is None:
            return None
        return first.pulsar.comment

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
        result = PulsarFoldResult.objects.accessible_to(instance.context.user).order_by("observation__duration").last()
        return result.observation.duration if result else None

    def resolve_min_plot_length(self, instance):
        result = (
            PulsarFoldResult.objects.accessible_to(instance.context.user).order_by("-observation__duration").last()
        )
        return result.observation.duration if result else None


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
        connection_class = PulsarFoldResultConnection

    # ForeignKey fields
    next_observation = graphene.Field(lambda: PulsarFoldResultNode)
    previous_observation = graphene.Field(lambda: PulsarFoldResultNode)
    observation = graphene.Field(ObservationNode)
    pipeline_run = graphene.Field(PipelineRunNode)
    project = graphene.Field(ProjectNode)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

    def resolve_images(self, info):
        """
        Check if user is allowed to access the images.
        """
        if not _observation_is_accessible(self.observation, info.context):
            return PipelineImage.objects.none()

        return self.images.all()

    def resolve_observation(self, info):
        return self.observation

    def resolve_pipeline_run(self, info):
        return self.pipeline_run

    def resolve_project(self, info):
        return self.observation.project

    def resolve_next_observation(self, info):
        """
        Find next observation.
        """
        next_obs = (
            PulsarFoldResult.objects.filter(
                observation__project__main_project=self.observation.project.main_project,
                pulsar__name=self.observation.pulsar.name,
                observation__utc_start__gt=self.observation.utc_start,
            )
            .order_by("observation__utc_start")
            .first()
        )
        return next_obs if next_obs else None

    def resolve_previous_observation(self, info):
        """
        Find previous observation.
        """
        prev_obs = (
            PulsarFoldResult.objects.filter(
                observation__project__main_project=self.observation.project.main_project,
                pulsar__name=self.observation.pulsar.name,
                observation__utc_start__lt=self.observation.utc_start,
            )
            .order_by("-observation__utc_start")
            .first()
        )
        return prev_obs if prev_obs else None


class PulsarFoldSummaryConnection(relay.Connection):
    class Meta:
        abstract = True

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Float()
    total_project_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum(edge.node.number_of_observations for edge in self.edges if edge.node.number_of_observations)

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum(edge.node.total_integration_hours for edge in self.edges), 1)

    def resolve_total_project_time(self, instance):
        if not self.edges:
            return 0
        total_seconds = sum(
            obs.duration
            for obs in Observation.objects.accessible_to(instance.context.user).filter(
                project__short=self.edges[0].node.most_common_project
            )
        )
        return int(total_seconds / 60 / 60)


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
        filter_fields = ["pulsar__name", "main_project__name"]
        interfaces = (relay.Node,)
        connection_class = PulsarFoldSummaryConnection

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    main_project = graphene.Field(MainProjectNode)


class PulsarSearchSummaryConnection(relay.Connection):
    class Meta:
        abstract = True

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Float()
    total_project_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum(edge.node.number_of_observations for edge in self.edges if edge.node.number_of_observations)

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum(edge.node.total_integration_hours for edge in self.edges), 1)

    def resolve_total_project_time(self, instance):
        if not self.edges:
            return 0
        total_seconds = sum(
            obs.duration
            for obs in Observation.objects.accessible_to(instance.context.user).filter(
                project__short=self.edges[0].node.most_common_project
            )
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
        filter_fields = ["pulsar__name", "main_project__name", "most_common_project__name"]
        interfaces = (relay.Node,)
        connection_class = PulsarSearchSummaryConnection

    # ForeignKey fields
    pulsar = graphene.Field(PulsarNode)
    main_project = graphene.Field(MainProjectNode)


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
        # Avoid ImageField in filter generation (django-filter can't infer it by default).
        filter_fields = {
            "pulsar_fold_result__id": ["exact"],
            "url": ["exact", "icontains"],
            "cleaned": ["exact"],
            "image_type": ["exact"],
            "resolution": ["exact"],
        }
        interfaces = (relay.Node,)

    # ForeignKey fields
    pulsar_fold_result = graphene.Field(PulsarFoldResultNode)

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.accessible_to(info.context.user)

    def resolve_pulsar_fold_result(self, info):
        if self.pulsar_fold_result.observation.is_restricted(info.context.user):
            return None
        return self.pulsar_fold_result


class ToaConnection(relay.Connection):
    class Meta:
        abstract = True

    all_projects = graphene.List(graphene.String)
    all_nchans = graphene.List(graphene.Int)
    total_badge_excluded_toas = graphene.Int()

    def resolve_all_projects(self, instance):
        if "pulsar" in instance.variable_values.keys():
            toa_project_query = Toa.objects.accessible_to(instance.context.user).filter(
                observation__pulsar__name=instance.variable_values["pulsar"]
            )
            if "mainProject" in instance.variable_values.keys():
                toa_project_query = toa_project_query.filter(
                    project__main_project__name__icontains=instance.variable_values["mainProject"]
                )
            return list(toa_project_query.values_list("project__short", flat=True).distinct())

        return []

    def resolve_all_nchans(self, instance):
        if "pulsar" in instance.variable_values.keys():
            toa_nchan_query = Toa.objects.accessible_to(instance.context.user).filter(
                observation__pulsar__name=instance.variable_values["pulsar"]
            )
            if "mainProject" in instance.variable_values.keys():
                toa_nchan_query = toa_nchan_query.filter(
                    project__main_project__name__icontains=instance.variable_values["mainProject"]
                )
            values = list(toa_nchan_query.values_list("obs_nchan", flat=True).distinct())
            return sorted(values)

        return []

    def resolve_total_badge_excluded_toas(self, instance):
        if "excludeBadges" not in instance.variable_values.keys():
            return 0

        queryset = (
            Toa.objects.accessible_to(instance.context.user)
            .select_related(
                "pipeline_run",
                "ephemeris",
                "template",
                "project",
                "pipeline_run__observation__calibration",
                "observation__pulsar",
                "observation__project__main_project",
            )
            .prefetch_related(
                "pipeline_run__observation__calibration__badges",
            )
            .all()
        )

        if "pipelineRunId" in instance.variable_values.keys():
            queryset = queryset.filter(pipeline_run__id=instance.variable_values["pipelineRunId"])

        if "pulsar" in instance.variable_values.keys():
            queryset = queryset.filter(observation__pulsar__name=instance.variable_values["pulsar"])

        if "mainProject" in instance.variable_values.keys():
            queryset = queryset.filter(
                observation__project__main_project__name__iexact=instance.variable_values["mainProject"]
            )

        if "projectShort" in instance.variable_values.keys() and instance.variable_values["projectShort"] != "":
            queryset = queryset.filter(project__short=instance.variable_values["projectShort"])

        if "dmCorrected" in instance.variable_values.keys():
            queryset = queryset.filter(dm_corrected=bool(instance.variable_values["dmCorrected"]))

        if "nsubType" in instance.variable_values.keys():
            queryset = queryset.filter(nsub_type=instance.variable_values["nsubType"])

        if "obsNchan" in instance.variable_values.keys():
            queryset = queryset.filter(obs_nchan=instance.variable_values["obsNchan"])

        if "obsNpol" in instance.variable_values.keys():
            queryset = queryset.filter(obs_npol=instance.variable_values["obsNpol"])
        #
        # Filter and observations with badges
        badge_filter = (
            Q(pipeline_run__badges__name__in=instance.variable_values["excludeBadges"])
            | Q(pipeline_run__observation__calibration__badges__name__in=instance.variable_values["excludeBadges"])
            | Q(snr__lt=instance.variable_values["minimumSNR"])
        )

        return queryset.filter(badge_filter).count()


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
            "nsub_type",
            "obs_nchan",
            "obs_npol",
            "binary_orbital_phase",
            "day_of_year",
            "residual_sec",
            "residual_sec_err",
            "residual_phase",
            "residual_phase_err",
        ]
        filter_fields = {
            "dm_corrected": ["exact"],
            "nsub_type": ["exact"],
            "obs_nchan": ["exact"],
        }
        interfaces = (relay.Node,)
        connection_class = ToaConnection

    # ForeignKey fields
    pipeline_run = graphene.Field(PipelineRunNode)
    observation = graphene.Field(ObservationNode)
    project = graphene.Field(ProjectNode)
    ephemeris = graphene.Field(EphemerisNode)
    template = graphene.Field(TemplateNode)

    nsub_type = graphene.String()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.accessible_to(info.context.user)

    def resolve_pipeline_run(self, info):
        if self.pipeline_run is None:
            return None
        if hasattr(self, "_pipeline_run_observation_is_accessible"):
            return self.pipeline_run if self._pipeline_run_observation_is_accessible else None
        if self.pipeline_run.observation.is_restricted(info.context.user):
            return None
        return self.pipeline_run

    def resolve_observation(self, info):
        if hasattr(self, "_observation_is_accessible"):
            return self.observation if self._observation_is_accessible else None
        if self.observation.is_restricted(info.context.user):
            return None
        return self.observation

    def resolve_project(self, info):
        if self.is_restricted(info.context.user):
            return None
        return self.project

    def resolve_ephemeris(self, info):
        if self.ephemeris is None:
            return None
        if hasattr(self, "_ephemeris_is_accessible"):
            return self.ephemeris if self._ephemeris_is_accessible else None
        if self.ephemeris.is_restricted(info.context.user):
            return None
        return self.ephemeris

    def resolve_template(self, info):
        if self.template is None:
            return None
        if hasattr(self, "_template_is_accessible"):
            return self.template if self._template_is_accessible else None
        if self.template.is_restricted(info.context.user):
            return None
        return self.template


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    # File-related fields
    files = relay.ConnectionField(
        FileConnection,
        path=graphene.String(required=True),
        recursive=graphene.Boolean(default_value=False),
        description="List files at the given path",
    )

    file_single_list = relay.ConnectionField(
        FileConnection,
        main_project=graphene.String(required=True),
        jname=graphene.String(required=True),
        utc=graphene.String(required=True),
        beam=graphene.Int(required=True),
        description="Get files for a specific pulsar observation",
    )

    file_pulsar_list = relay.ConnectionField(
        FileConnection,
        main_project=graphene.String(required=True),
        jname=graphene.String(required=True),
        description="Get files for a pulsar",
    )

    pulsar = DjangoFilterConnectionField(PulsarNode)

    telescope = DjangoFilterConnectionField(TelescopeNode)

    @login_required
    def resolve_telescope(self, info, **kwargs):
        queryset = Telescope.objects.all()

        name = kwargs.get("name")
        if name:
            queryset = queryset.filter(name=name)

        return queryset

    main_project = DjangoFilterConnectionField(MainProjectNode)

    @login_required
    def resolve_main_project(self, info, **kwargs):
        return MainProject.objects.all()

    project = DjangoFilterConnectionField(ProjectNode)

    @login_required
    def resolve_project(self, info, **kwargs):
        return Project.objects.all()

    project_configuration = DjangoFilterConnectionField(ProjectNode, max_limit=None)

    def resolve_project_configuration(self, info, **kwargs):
        return (
            Project.objects.filter(is_visible_on_frontend=True)
            .select_related("main_project__telescope")
            .order_by("display_order", "id")
        )

    ephemeris = DjangoFilterConnectionField(EphemerisNode)

    @login_required
    def resolve_ephemeris(self, info, **kwargs):
        return Ephemeris.objects.accessible_to(info.context.user)

    template = DjangoFilterConnectionField(TemplateNode)

    @login_required
    def resolve_template(self, info, **kwargs):
        return Template.objects.accessible_to(info.context.user)

    calibration = DjangoFilterConnectionField(CalibrationNode, filterset_class=CalibrationFilterSet)

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
    def resolve_calibration(self, info, **kwargs):
        return Calibration.objects.filter(n_observations__gt=0)

    observation = DjangoFilterConnectionField(ObservationNode, filterset_class=ObservationFilterSet)

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
    def resolve_observation(self, info, **kwargs):
        return Observation.objects.select_related(
            "pulsar", "telescope", "project__main_project", "calibration", "ephemeris"
        ).accessible_to(info.context.user)

    observation_summary = DjangoFilterConnectionField(
        ObservationSummaryNode,
        filterset_class=ObservationSummaryFilterSet,
    )

    pipeline_run = DjangoFilterConnectionField(PipelineRunNode)

    @login_required
    def resolve_pipeline_run(self, info, **kwargs):
        if pipeline_run_id := kwargs.get("id"):
            try:
                PipelineRun.objects.get(id=pipeline_run_id)
            except PipelineRun.DoesNotExist:
                return GraphQLError("Pipeline run doesn't exist")

        return PipelineRun.objects.select_related("observation", "ephemeris", "template").accessible_to(
            info.context.user
        )

    pulsar_fold_result = DjangoFilterConnectionField(
        PulsarFoldResultNode,
        filterset_class=PulsarFoldResultFilterSet,
        max_limit=5000,
    )

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
    def resolve_pulsar_fold_result(self, info, **kwargs):
        queryset = (
            PulsarFoldResult.objects.prefetch_related(
                "pipeline_run__badges",
                "pipeline_run__observation__calibration__badges",
            )
            .select_related(
                "observation__project",
                "observation__ephemeris",
                "observation__calibration",
                "pipeline_run",
                "pipeline_run__observation",
                "pipeline_run__observation__ephemeris",
                "pipeline_run__observation__calibration",
            )
            .all()
        )

        return queryset

    pulsar_fold_summary = DjangoFilterConnectionField(
        PulsarFoldSummaryNode,
        filterset_class=PulsarFoldSummaryFilterSet,
        max_limit=5000,
    )

    pulsar_search_summary = DjangoFilterConnectionField(
        PulsarSearchSummaryNode,
        filterset_class=PulsarSearchSummaryFilterSet,
        max_limit=5000,
    )

    pipeline_image = DjangoFilterConnectionField(PipelineImageNode)

    @login_required
    def resolve_pipeline_image(self, info, **kwargs):
        return PipelineImage.objects.accessible_to(info.context.user)

    toa = DjangoFilterConnectionField(
        ToaNode,
        filterset_class=ToaFilterSet,
    )

    @login_required
    def resolve_toa(self, info, **kwargs):
        queryset = Toa.objects.select_related(
            "pipeline_run",
            "pipeline_run__observation",
            "observation",
            "ephemeris",
            "template",
            "project",
        ).all()

        return queryset.accessible_to(info.context.user).order_by("mjd")

    badge = DjangoFilterConnectionField(BadgeNode)

    @login_required
    def resolve_badge(self, info, **kwargs):
        return Badge.objects.all()

    @login_required
    @user_passes_test(lambda user: user.is_unrestricted())
    def resolve_files(self, info, path, recursive=False, **kwargs):
        """Get list of files at specified path"""
        success, result = get_file_list(path, recursive)

        if not success:
            return []

        return [
            FileNode(
                id=file["fileName"],
                path=file["path"],
                file_name=file["fileName"],
                file_size=str(file["fileSize"]),  # Convert to string for GraphQL
                is_directory=file["isDirectory"],
            )
            for file in result
        ]

    @login_required
    @user_passes_test(lambda user: user.is_unrestricted())
    def resolve_file_single_list(self, info, **kwargs):
        """Get files for a specific pulsar observation"""
        try:
            # Parse the datetime and make it timezone-aware (UTC)
            naive_dt = datetime.strptime(kwargs.get("utc"), "%Y-%m-%d-%H:%M:%S")
            aware_dt = naive_dt.replace(tzinfo=dt_timezone.utc)
            pulsar_fold_result = PulsarFoldResult.objects.get(
                pulsar__name=kwargs.get("jname"),
                observation__utc_start=aware_dt,
                observation__beam=kwargs.get("beam"),
            )

            # Only allow files if the user has access to this fold pulsar observation
            if not pulsar_fold_result.observation.is_restricted(info.context.user):
                if not pulsar_fold_result.observation.project.allow_downloads:
                    return []
                # Construct path in the local file system
                path = f"/{kwargs.get('jname')}/{kwargs.get('utc')}/{kwargs.get('beam')}/"

                success, files = get_file_list(path, True)

                if success:
                    return [
                        FileNode(
                            id=file["fileName"],
                            path=file["path"],
                            file_name=file["fileName"],
                            file_size=str(file["fileSize"]),
                            is_directory=file["isDirectory"],
                        )
                        for file in files
                        if file["path"].endswith(".ar") and not file["isDirectory"]
                    ]
        except Exception as e:
            print(f"Error retrieving file list: {str(e)}")

        return []

    @login_required
    @user_passes_test(lambda user: user.is_unrestricted())
    def resolve_file_pulsar_list(self, info, **kwargs):
        """Get files for a pulsar"""
        projects_for_main_project = Project.objects.filter(main_project__name__iexact=kwargs.get("main_project"))
        has_downloadable_project = projects_for_main_project.filter(allow_downloads=True).exists()

        if not has_downloadable_project:
            return []

        # Construct path in the local file system
        path = f"/{kwargs.get('jname')}/"

        success, files = get_file_list(path, True)

        if success:
            return [
                FileNode(
                    id=file["fileName"],
                    path=file["path"],
                    file_name=file["fileName"],
                    file_size=str(file["fileSize"]),
                    is_directory=file["isDirectory"],
                )
                for file in files
                if file["path"].endswith(".ar") and not file["isDirectory"]
            ]

        return []
