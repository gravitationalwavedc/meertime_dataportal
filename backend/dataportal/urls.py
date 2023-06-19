from django.urls import path, re_path, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers

from .logic import get_trapum_filters, get_meertime_filters

from . import views

router = routers.DefaultRouter()
router.register(r'upload/template', views.UploadTemplate, basename="upload_template")
router.register(r'upload/image',    views.UploadImage,    basename="upload_image")

urlpatterns = [
    path("", include(router.urls)),
]
