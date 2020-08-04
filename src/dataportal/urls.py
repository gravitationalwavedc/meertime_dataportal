from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="dataportal-home"),
    re_path(
        r"^(?P<psr>[BJ][0-2][0-9]*[-+][0-9]*[a-zA-Z]*)$", views.DetailView.as_view(), name="dataportal-psr-detail",
    ),
]
