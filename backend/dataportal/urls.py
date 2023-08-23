from django.urls import path, re_path, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'upload/template', views.UploadTemplate,      basename="upload_template")
router.register(r'upload/image',    views.UploadPipelineImage, basename="upload_image")

urlpatterns = [
    path("", include(router.urls)),
]
