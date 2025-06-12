from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"api/upload/template", views.UploadTemplate, basename="upload_template")
router.register(r"api/upload/image", views.UploadPipelineImage, basename="upload_image")

urlpatterns = [
    path("", include(router.urls)),
    path("download/<path:file_path>", views.download_file, name="download_file"),
]
