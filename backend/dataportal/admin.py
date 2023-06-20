from django.contrib import admin
from .models import Pulsar, MainProject, Project, Calibration, Observation, Template, PipelineRun, Ephemeris

admin.site.register(Pulsar)
admin.site.register(MainProject)
admin.site.register(Project)
admin.site.register(Calibration)
admin.site.register(Observation)
admin.site.register(Template)
admin.site.register(PipelineRun)
admin.site.register(Ephemeris)
