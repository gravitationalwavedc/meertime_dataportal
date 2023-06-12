from django.contrib import admin
from .models import Pulsar, MainProject, Project, Calibration, Observation, Session

admin.site.register(Pulsar)
admin.site.register(MainProject)
admin.site.register(Project)
admin.site.register(Calibration)
admin.site.register(Observation)
admin.site.register(Session)
