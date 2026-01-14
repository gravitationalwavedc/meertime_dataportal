import math
from collections import Counter
from datetime import datetime, timezone as dt_timezone

import graphene
from astropy.time import Time
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Subquery
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
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


class PulsarNode(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = [
            "name",
            "comment",
        ]
        interfaces = (relay.Node,)


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
            "badges",
        ]
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    id_int = graphene.Int()

    def resolve_id_int(self, info):
        return self.id

    @classmethod
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
        return self.is_restricted(info.context.user)

    def resolve_mode_duration(self, info):
        obs = Observation.objects.all()
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
        # Sort by count and then by value to get shortest duration on draws
        duration_count_pairs = sorted(duration_count_pairs, key=lambda x: (-x[1], x[0]))
        return duration_count_pairs[0][0]


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

    def resolve_dm_err(self, info):
        """
        Return None for any non-scalar dm_err values (inf, -inf, nan).
        GraphQL Float scalar type cannot represent these values.
        """
        return None if self.dm_err is None or math.isinf(self.dm_err) or math.isnan(self.dm_err) else self.dm_err


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
    next_observation = graphene.Field(lambda: PulsarFoldResultNode)
    previous_observation = graphene.Field(lambda: PulsarFoldResultNode)
    observation = graphene.Field(ObservationNode)
    pipeline_run = graphene.Field(PipelineRunNode)
    project = graphene.Field(ProjectNode)

    def resolve_images(self, info):
        """
        Check if user is allowed to access the images.
        """
        if self.observation.is_restricted(info.context.user):
            return []

        return self.images.all()

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
        project_short=graphene.String(default_value="All"),
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
    toas_link = graphene.String()
    all_projects = graphene.List(graphene.String)
    most_common_project = graphene.String()
    all_nchans = graphene.List(graphene.Int)
    timing_residual_plot_data = graphene.Field(
        graphene.List(TimingResidualPlotDataType),
        pulsar=graphene.String(required=True),
        main_project=graphene.String(default_value="Meertime"),
        project_short=graphene.String(default_value="All"),
        nsub_type=graphene.String(default_value="1"),
        obs_nchan=graphene.Int(default_value=32),
        exclude_badges=graphene.List(graphene.String, default_value=[]),
        minimumSNR=graphene.Float(default_value=8),
        dm_corrected=graphene.Boolean(default_value=False),
    )

    class Meta:
        node = PulsarFoldResultNode

    def resolve_total_toa(self, instance, **kwargs):
        toas = Toa.objects.filter(
            observation__pulsar__name=kwargs.get("pulsar"),
            observation__project__main_project__name__iexact=kwargs.get("main_project"),
            dm_corrected=False,
            obs_nchan=32,
            nsub_type=kwargs.get("nsub_type"),
        )

        if kwargs.get("project_short") != "All":
            toas = toas.filter(project__short=kwargs.get("project_short"))

        return toas.count()

    def resolve_most_common_project(self, instance):
        return self.iterable.first().pulsar.pulsarfoldsummary_set.first().most_common_project

    def resolve_timing_residual_plot_data(self, _, **kwargs):
        toas = (
            Toa.objects.select_related(
                "pipeline_run__badges",
                "pipeline_run__observation__calibration__badges",
                "observation__badges",
                "observation__pulsar",
                "observation__project__main_project",
                "observation",
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

        if kwargs.get("project_short") != "All":
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
                Toa.objects.filter(observation__pulsar__name=instance.variable_values["pulsar"])
                .values_list("project__short", flat=True)
                .distinct()
            )
        else:
            return []

    def resolve_all_nchans(self, instance):
        if "pulsar" not in instance.variable_values.keys():
            return []

        return list(
            Toa.objects.filter(observation__pulsar__name=instance.variable_values["pulsar"])
            .values_list("obs_nchan", flat=True)
            .order_by("obs_nchan")
            .distinct()
        )

    def resolve_toas_link(self, instance):
        return self.iterable.first().pipeline_run.toas_download_link

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
           - Skip if observation.project is None
           - Skip if pipeline_run.ephemeris is None
           - Skip if ephemeris.project is "PTUSE"
           - Skip if pipeline_run has no TOAs

        2. Sort remaining PulsarFoldResults by pipeline_run.created_at (most recent first)

        3. For each PulsarFoldResult (in order):
           a. Check if ephemeris is embargoed:
              embargo_end = ephemeris.created_at + ephemeris.project.embargo_period
              is_embargoed = (embargo_end >= now)

           b. Grant access if:
              - Ephemeris is NOT embargoed (public), OR
              - User is a superuser, OR
              - User is a member of ephemeris.project

           c. If access granted: RETURN (ephemeris, pfr)
           d. If access denied: CONTINUE to next PulsarFoldResult

        4. If no accessible ephemeris found: RETURN (None, None)

        Key Points:
        -----------
        - Only one PulsarFoldResult exists for each observation, it is updated with the most recent pipeline run automatically (not here). These are the PFR's that we are iterating on
        - We reorder the PulsarFoldResults (equivalent to observation list with processing results) on the FoldDetail page by which one has had the most recent pipeline run
        - Embargo is based on ephemeris.created_at + ephemeris.project.embargo_period
        - Membership is checked against ephemeris.project (NOT observation.project)
        """
        user = instance.context.user
        now = timezone.now()

        # Filter to valid pipeline fold results from the iterable
        valid_pfrs = []
        for pfr in self.iterable:
            # Skip observations without projects
            if pfr.observation.project is None or pfr.observation.project.short is None:
                continue
            # Skip pipeline runs without ephemeris
            if pfr.pipeline_run.ephemeris is None:
                continue
            # Skip PTUSE project ephemerides
            if pfr.pipeline_run.ephemeris.project.short.upper() == "PTUSE":
                continue
            # Skip pipeline runs without TOAs
            if not Toa.objects.filter(pipeline_run=pfr.pipeline_run).exists():
                continue
            valid_pfrs.append(pfr)

        if not valid_pfrs:
            return None, None, False

        # Sort by pipeline run created_at (most recent first)
        valid_pfrs.sort(key=lambda x: x.pipeline_run.created_at, reverse=True)

        # Find the first pipeline run the user can access
        for pfr in valid_pfrs:
            pipeline_run = pfr.pipeline_run
            ephemeris = pipeline_run.ephemeris
            ephemeris_project = ephemeris.project

            # Check if the ephemeris is embargoed
            # Embargo is based on ephemeris creation date + ephemeris project's embargo period
            embargo_end_date = ephemeris.created_at + ephemeris_project.embargo_period
            is_embargoed = embargo_end_date >= now

            # Grant access if:
            # 1. Ephemeris is not embargoed (public data), OR
            # 2. User is a superuser, OR
            # 3. User is a member of the ephemeris's project
            if not is_embargoed:
                return ephemeris, pfr, True

            if user.is_authenticated and user.is_superuser:
                return ephemeris, pfr, True

            if user.is_authenticated:
                if ProjectMembership.objects.filter(
                    user=user,
                    project=ephemeris_project,
                    is_active=True,
                ).exists():
                    return ephemeris, pfr, True

            # User doesn't have access to this embargoed ephemeris, continue to next

        # No accessible ephemeris found, but valid ephemerides do exist
        return None, None, True

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
           - Skip if observation.project is None
           - Skip if pipeline_run.template is None
           - Skip if template.project is "PTUSE"
           - Skip if pipeline_run has no TOAs

        2. Sort remaining PulsarFoldResults by pipeline_run.created_at (most recent first)

        3. For each PulsarFoldResult (in order):
           a. Check if template is restricted using template.is_restricted(user)

           b. Grant access if not restricted (handles authentication, embargo, and membership)

           c. If access granted: RETURN (template, pfr)
           d. If access denied: CONTINUE to next PulsarFoldResult

        4. If no accessible template found: RETURN (None, None)

        Key Points:
        -----------
        - Only one PulsarFoldResult exists for each observation, it is updated with the most recent pipeline run automatically
        - We reorder the PulsarFoldResults by which one has had the most recent pipeline run
        - Embargo is based on template.created_at + template.project.embargo_period
        - Membership is checked against template.project
        """
        user = instance.context.user

        # Filter to valid pipeline fold results from the iterable
        valid_pfrs = []
        for pfr in self.iterable:
            # Skip observations without projects
            if pfr.observation.project is None or pfr.observation.project.short is None:
                continue
            # Skip pipeline runs without template
            if pfr.pipeline_run.template is None:
                continue
            # Skip PTUSE project templates
            if pfr.pipeline_run.template.project.short.upper() == "PTUSE":
                continue
            # Skip pipeline runs without TOAs
            if not Toa.objects.filter(pipeline_run=pfr.pipeline_run).exists():
                continue
            valid_pfrs.append(pfr)

        if not valid_pfrs:
            return None, None, False

        # Sort by pipeline run created_at (most recent first)
        valid_pfrs.sort(key=lambda x: x.pipeline_run.created_at, reverse=True)

        # Find the first pipeline run the user can access
        for pfr in valid_pfrs:
            pipeline_run = pfr.pipeline_run
            template = pipeline_run.template

            # Use template's is_restricted method
            # (handles authentication, embargo checking, and project membership)
            if not template.is_restricted(user):
                return template, pfr, True

            # User doesn't have access to this template, continue to next

        # No accessible template found, but valid templates do exist
        return None, None, True

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
            queryset = (
                PulsarFoldResult.objects.select_related("pipeline_run")
                .prefetch_related("pipeline_run__badges")
                .select_related("pipeline_run__observation__calibration")
                .prefetch_related("pipeline_run__observation__calibration__badges")
                .all()
            )
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
            # Filter and observations with badges or below minimum SNR
            badge_snr_filter = (
                Q(pipeline_run__badges__name__in=instance.variable_values["excludeBadges"])
                | Q(pipeline_run__observation__calibration__badges__name__in=instance.variable_values["excludeBadges"])
                | Q(pipeline_run__sn__lt=instance.variable_values["minimumSNR"])
            )
            return queryset.filter(badge_snr_filter).count()
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
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class PulsarFoldSummaryConnection(relay.Connection):
    class Meta:
        node = PulsarFoldSummaryNode

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
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class PulsarSearchSummaryConnection(relay.Connection):
    class Meta:
        node = PulsarSearchSummaryNode

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
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class PipelineImageConnection(relay.Connection):
    class Meta:
        node = PipelineImageNode


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

    # ForeignKey fields
    pipeline_run = graphene.Field(PipelineRunNode)
    ephemeris = graphene.Field(EphemerisNode)
    template = graphene.Field(TemplateNode)

    nsub_type = graphene.String()


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

        return []

    def resolve_all_nchans(self, instance):
        if "pulsar" in instance.variable_values.keys():
            toa_nchan_query = Toa.objects.filter(observation__pulsar__name=instance.variable_values["pulsar"])
            if "mainProject" in instance.variable_values.keys():
                toa_nchan_query = toa_nchan_query.filter(
                    project__main_project__name__icontains=instance.variable_values["mainProject"]
                )
            return list(toa_nchan_query.values_list("obs_nchan", flat=True).distinct())

        return []

    def resolve_total_badge_excluded_toas(self, instance):
        if "excludeBadges" not in instance.variable_values.keys():
            return 0

        queryset = Toa.objects.select_related(
            "pipeline_run",
            "ephemeris",
            "template",
            "project",
            "pipeline_run__observation__calibration__badges",
            "observation__pulsar",
            "observation__project__main_project",
        ).all()

        if "pipelineRunId" in instance.variable_values.keys():
            queryset = queryset.filter(pipeline_run__id=instance.variable_values["pipelineRunId"])

        if "pulsar" in instance.variable_values.keys():
            queryset = queryset.filter(observation__pulsar__name=instance.variable_values["pulsar"])

        if "mainProject" in instance.variable_values.keys():
            queryset = queryset.filter(
                observation__project__main_project__name__iexact=instance.variable_values["mainProject"]
            )

        if "projectShort" in instance.variable_values.keys() and instance.variable_values["projectShort"] != "All":
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

    # Original pulsar field
    pulsar = relay.ConnectionField(
        PulsarConnection,
        name=graphene.String(),
    )

    @login_required
    def resolve_pulsar(self, info, **kwargs):
        if name := kwargs.get("name"):
            try:
                return [Pulsar.objects.get(name=name)]
            except Pulsar.DoesNotExist:
                return GraphQLError("Pulsar doesn't exist")

        return Pulsar.objects.all()

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

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
    def resolve_calibration(self, info, **kwargs):
        queryset = Calibration.objects.filter(n_observations__gt=0)

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

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
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

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
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
        if pipeline_run_id := kwargs.get("id"):
            try:
                PipelineRun.objects.get(id=pipeline_run_id)
            except PipelineRun.DoesNotExist:
                return GraphQLError("Pipeline run doesn't exist")

        return PipelineRun.objects.all()

    pulsar_fold_result = relay.ConnectionField(
        PulsarFoldResultConnection,
        pulsar=graphene.String(),
        mainProject=graphene.String(),
        utcStart=graphene.String(),
        beam=graphene.Int(),
        excludeBadges=graphene.List(graphene.String),
        minimumSNR=graphene.Float(),
        utcStartGte=graphene.String(),
        utcStartLte=graphene.String(),
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

        if pulsar_name := kwargs.get("pulsar"):
            queryset = queryset.filter(pulsar__name=pulsar_name)

        if main_project_name := kwargs.get("mainProject"):
            queryset = queryset.filter(observation__project__main_project__name__iexact=main_project_name)

        if utc_start := kwargs.get("utcStart"):
            # Parse the datetime and make it timezone-aware (UTC)
            naive_dt = datetime.strptime(utc_start, "%Y-%m-%d-%H:%M:%S")
            aware_dt = naive_dt.replace(tzinfo=dt_timezone.utc)
            queryset = queryset.filter(observation__utc_start=aware_dt)

        if beam := kwargs.get("beam"):
            queryset = queryset.filter(observation__beam=beam)

        if exclude_badges := kwargs.get("excludeBadges"):
            queryset = queryset.exclude(pipeline_run__badges__name__in=exclude_badges).exclude(
                pipeline_run__observation__calibration__badges__name__in=exclude_badges
            )

        if minimumSNR := kwargs.get("minimumSNR"):
            queryset = queryset.filter(pipeline_run__sn__gte=minimumSNR)

        if utc_start_gte := kwargs.get("utcStartGte"):
            queryset = queryset.filter(observation__utc_start__gte=utc_start_gte)

        if utc_start_lte := kwargs.get("utcStartLte"):
            queryset = queryset.filter(observation__utc_start__lte=utc_start_lte)

        return queryset

    pulsar_fold_summary = relay.ConnectionField(
        PulsarFoldSummaryConnection,
        main_project=graphene.String(),
        most_common_project=graphene.String(),
        project=graphene.String(),
        band=graphene.String(),
    )

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
    def resolve_pulsar_fold_summary(self, info, **kwargs):
        return PulsarFoldSummary.get_query(**kwargs)

    pulsar_search_summary = relay.ConnectionField(
        PulsarSearchSummaryConnection,
        main_project=graphene.String(),
        most_common_project=graphene.String(),
        project=graphene.String(),
        band=graphene.String(),
    )

    # This requires public access for the frontend web app to work.
    # Don't put behind a login
    def resolve_pulsar_search_summary(self, info, **kwargs):
        return PulsarSearchSummary.get_query(**kwargs)

    pipeline_image = relay.ConnectionField(
        PipelineImageConnection,
    )

    @login_required
    def resolve_pipeline_image(self, info, **kwargs):
        return PipelineImage.objects.all()

    toa = relay.ConnectionField(
        ToaConnection,
        pipelineRunId=graphene.Int(),
        pulsar=graphene.String(),
        mainProject=graphene.String(),
        projectShort=graphene.String(),
        dmCorrected=graphene.Boolean(),
        nsubType=graphene.String(),
        obsNchan=graphene.Int(),
        obsNpol=graphene.Int(),
        excludeBadges=graphene.List(graphene.String),
        minimumSNR=graphene.Float(),
        utcStartGte=graphene.String(),
        utcStartLte=graphene.String(),
    )

    @login_required
    def resolve_toa(self, info, **kwargs):
        queryset = Toa.objects.select_related(
            "pipeline_run",
            "ephemeris",
            "template",
            "project",
        ).all()

        if pipelineRunId := kwargs.get("pipelineRunId"):
            queryset = queryset.select_related("pipeline_run").filter(pipeline_run__id=pipelineRunId)

        if pulsar_name := kwargs.get("pulsar"):
            queryset = queryset.select_related("observation__pulsar").filter(observation__pulsar__name=pulsar_name)

        if main_project_name := kwargs.get("mainProject"):
            queryset = queryset.select_related("observation__project__main_project").filter(
                observation__project__main_project__name__iexact=main_project_name
            )

        project_short = kwargs.get("projectShort")
        if project_short and project_short != "All":
            queryset = queryset.select_related("project").filter(project__short=project_short)

        dm_corrected = kwargs.get("dmCorrected")
        if dm_corrected is not None:
            queryset = queryset.filter(dm_corrected=bool(dm_corrected))

        nsub_type = kwargs.get("nsubType")
        if nsub_type is not None:
            queryset = queryset.filter(nsub_type=nsub_type)

        if obs_nchan := kwargs.get("obsNchan"):
            queryset = queryset.filter(obs_nchan=obs_nchan)

        if obs_npol := kwargs.get("obsNpol"):
            queryset = queryset.filter(obs_npol=obs_npol)

        if exclude_badges := kwargs.get("excludeBadges"):
            queryset = queryset.exclude(pipeline_run__badges__name__in=exclude_badges).exclude(
                pipeline_run__observation__calibration__badges__name__in=exclude_badges
            )

        if minimumSNR := kwargs.get("minimumSNR"):
            queryset = queryset.filter(snr__gte=minimumSNR)

        if utc_start_gte := kwargs.get("utcStartGte"):
            queryset = queryset.filter(observation__utc_start__gte=utc_start_gte)

        if utc_start_lte := kwargs.get("utcStartLte"):
            queryset = queryset.filter(observation__utc_start__lte=utc_start_lte)

        return queryset.order_by("mjd")

    badge = relay.ConnectionField(
        BadgeConnection,
    )

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
                # Construct path in the local file system
                path = f"/{kwargs.get('jname')}/{kwargs.get('utc')}/{kwargs.get('beam')}/"
                if kwargs.get("main_project") == "MONSPSR":
                    raise Exception("MONSPSR is unusable until the file structure is fixed.")
                    path = f"/post/{kwargs.get('jname')}/{kwargs.get('utc')}/"

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
        # Construct path in the local file system
        path = f"/{kwargs.get('jname')}/"
        if kwargs.get("main_project") == "MONSPSR":
            raise Exception("MONSPSR is unusable until the file structure is fixed.")
            path = f"/post/{kwargs.get('jname')}/"

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
