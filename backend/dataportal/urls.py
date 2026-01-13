from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"api/upload/template", views.UploadTemplate, basename="upload_template")
router.register(r"api/upload/image", views.UploadPipelineImage, basename="upload_image")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "download/<str:jname>/<str:observation_timestamp>/<int:beam>/<str:file_type>",
        views.download_observation_files,
        name="download_observation_files",
    ),
    path(
        "download/<str:jname>/<str:file_type>",
        views.download_pulsar_files,
        name="download_pulsar_files",
    ),
    path(
        "media/<path:file_path>",
        views.serve_protected_media,
        name="serve_protected_media",
    ),
]
