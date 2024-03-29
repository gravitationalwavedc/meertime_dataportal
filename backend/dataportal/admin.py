from django.contrib import admin
from .models import (
    Pulsar,
    Telescope,
    MainProject,
    Project,
    Ephemeris,
    Template,
    Calibration,
    Observation,
    ObservationSummary,
    PipelineRun,
    PulsarFoldResult,
    PulsarFoldSummary,
    PulsarSearchSummary,
    PipelineImage,
    Toa,
)


@admin.register(Pulsar)
class PulsarAdmin(admin.ModelAdmin):
    search_fields = ["name"]


admin.site.register(Telescope)
admin.site.register(MainProject)
admin.site.register(Project)
admin.site.register(Ephemeris)
admin.site.register(Template)
admin.site.register(Calibration)
admin.site.register(Observation)
admin.site.register(ObservationSummary)
admin.site.register(PipelineRun)
admin.site.register(PulsarFoldResult)
admin.site.register(PulsarFoldSummary)
admin.site.register(PulsarSearchSummary)
admin.site.register(PipelineImage)
admin.site.register(Toa)
