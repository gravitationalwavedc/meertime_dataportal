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
    PipelineImage,
    PipelineFile,
    Toa,
    Residual,
)

admin.site.register(Pulsar)
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
admin.site.register(PipelineImage)
admin.site.register(PipelineFile)
admin.site.register(Toa)
admin.site.register(Residual)

