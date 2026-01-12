from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
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
    ProjectMembershipRequest,
    Pulsar,
    PulsarFoldResult,
    PulsarFoldSummary,
    PulsarSearchSummary,
    Telescope,
    Template,
    Toa,
)


@admin.register(Pulsar)
class PulsarAdmin(admin.ModelAdmin):
    list_display = ["name", "comment"]
    search_fields = ["name"]


@admin.register(Telescope)
class TelescopeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(MainProject)
class MainProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "telescope"]
    search_fields = ["name"]
    list_filter = ["telescope"]


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    readonly_fields = ["joined_at"]
    list_select_related = ["user"]
    autocomplete_fields = ["user", "approved_by"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["code", "short", "description", "main_project", "embargo_period"]
    search_fields = ["code", "short", "description"]
    list_filter = ["main_project"]
    inlines = [ProjectMembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "role", "is_active", "joined_at", "approved_by"]
    list_filter = ["role", "is_active", "joined_at", "project"]
    search_fields = ["user__username", "user__email", "project__code", "project__short"]
    autocomplete_fields = ["user", "project", "approved_by"]
    readonly_fields = ["joined_at"]
    list_select_related = ["user", "project", "approved_by"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "project", "approved_by")


@admin.register(ProjectMembershipRequest)
class ProjectMembershipRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "status", "requested_at", "message"]
    list_filter = ["status", "requested_at"]
    search_fields = ["user__username", "user__email", "project__code", "project__short", "message"]
    readonly_fields = ["requested_at"]
    autocomplete_fields = ["user", "project"]
    list_select_related = ["user", "project"]


@admin.register(Ephemeris)
class EphemerisAdmin(admin.ModelAdmin):
    list_display = ["pulsar", "project", "p0", "dm", "valid_from", "valid_to", "created_at"]
    search_fields = ["pulsar__name", "project__code", "project__short"]
    list_filter = ["project", "created_at"]
    readonly_fields = ["created_at", "ephemeris_hash"]
    autocomplete_fields = ["pulsar", "project", "created_by"]


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ["pulsar", "project", "band", "created_at", "template_hash"]
    search_fields = ["pulsar__name", "project__code", "project__short"]
    list_filter = ["project", "band", "created_at"]
    readonly_fields = ["created_at", "template_hash"]
    autocomplete_fields = ["pulsar", "project", "created_by"]


class ObservationInline(admin.TabularInline):
    model = Observation
    extra = 0
    can_delete = False
    fields = [
        "observation_link",
        "utc_start",
        "pulsar",
        "project",
        "telescope",
        "band",
        "obs_type",
        "duration",
        "beam",
    ]
    readonly_fields = [
        "observation_link",
        "utc_start",
        "pulsar",
        "project",
        "telescope",
        "band",
        "obs_type",
        "duration",
        "beam",
    ]

    def observation_link(self, obj):
        if obj.id:
            url = reverse("admin:dataportal_observation_change", args=[obj.id])
            return format_html('<a href="{}">Edit</a>', url)
        return "-"

    observation_link.short_description = "Edit"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Calibration)
class CalibrationAdmin(admin.ModelAdmin):
    list_display = ["id", "schedule_block_id", "calibration_type", "start", "end", "n_observations", "all_projects"]
    search_fields = ["schedule_block_id", "all_projects"]
    list_filter = ["calibration_type", "start"]
    readonly_fields = [
        "start",
        "end",
        "all_projects",
        "n_observations",
        "n_ant_min",
        "n_ant_max",
        "total_integration_time_seconds",
    ]
    filter_horizontal = ["badges"]
    inlines = [ObservationInline]


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ["utc_start", "pulsar", "project", "telescope", "band", "obs_type", "duration", "beam"]
    search_fields = ["pulsar__name", "project__code", "project__short"]
    list_filter = ["project", "telescope", "band", "obs_type", "utc_start"]
    readonly_fields = ["ephemeris", "day_of_year", "binary_orbital_phase", "embargo_end_date", "band"]
    autocomplete_fields = ["pulsar", "project"]
    filter_horizontal = ["badges"]


@admin.register(ObservationSummary)
class ObservationSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "pulsar",
        "main_project",
        "project",
        "obs_type",
        "band",
        "observations",
        "observation_hours",
        "timespan_days",
    ]
    search_fields = ["pulsar__name", "project__code", "project__short"]
    list_filter = ["main_project", "project", "obs_type", "band"]


@admin.register(PipelineRun)
class PipelineRunAdmin(admin.ModelAdmin):
    list_display = ["id", "observation", "pipeline_name", "pipeline_version", "job_state", "created_at", "sn", "dm"]
    search_fields = ["pipeline_name", "created_by"]
    list_filter = ["job_state", "pipeline_name", "created_at"]
    readonly_fields = ["observation", "ephemeris", "template", "created_at"]
    filter_horizontal = ["badges"]


@admin.register(PulsarFoldResult)
class PulsarFoldResultAdmin(admin.ModelAdmin):
    list_display = ["id", "pulsar", "observation", "pipeline_run"]
    search_fields = ["pulsar__name"]
    autocomplete_fields = ["pulsar", "observation", "pipeline_run"]


@admin.register(PulsarFoldSummary)
class PulsarFoldSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "pulsar",
        "main_project",
        "latest_observation",
        "number_of_observations",
        "timespan",
        "last_sn",
        "highest_sn",
    ]
    search_fields = ["pulsar__name", "most_common_project", "all_projects"]
    list_filter = ["main_project"]
    readonly_fields = [
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
        "all_projects",
        "most_common_project",
    ]


@admin.register(PulsarSearchSummary)
class PulsarSearchSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "pulsar",
        "main_project",
        "latest_observation",
        "number_of_observations",
        "timespan",
        "total_integration_hours",
    ]
    search_fields = ["pulsar__name", "most_common_project", "all_projects"]
    list_filter = ["main_project"]
    readonly_fields = [
        "first_observation",
        "latest_observation",
        "timespan",
        "number_of_observations",
        "total_integration_hours",
        "last_integration_minutes",
        "all_bands",
        "all_projects",
        "most_common_project",
    ]


@admin.register(PipelineImage)
class PipelineImageAdmin(admin.ModelAdmin):
    list_display = ["id", "pulsar_fold_result", "image_type", "resolution", "cleaned"]
    list_filter = ["image_type", "resolution", "cleaned"]
    readonly_fields = ["pulsar_fold_result", "url"]


@admin.register(Toa)
class ToaAdmin(admin.ModelAdmin):
    list_display = ["id", "observation", "project", "mjd", "freq_MHz", "snr", "dm_corrected", "nsub_type"]
    search_fields = ["project__code", "project__short", "telescope"]
    list_filter = ["project", "dm_corrected", "nsub_type"]
    readonly_fields = [
        "day_of_year",
        "binary_orbital_phase",
        "residual_sec",
        "residual_sec_err",
        "residual_phase",
        "residual_phase_err",
    ]
    autocomplete_fields = ["pipeline_run", "observation", "project", "ephemeris", "template"]
