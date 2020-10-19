from django.urls import path, re_path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path("", login_required(views.FoldView.as_view()), name="fold"),
    path("search/", login_required(views.SearchmodeView.as_view()), name="search"),
    path("fluxcal/", login_required(views.FoldView.as_view()), name="fluxcal"),
    re_path(
        r"^(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)[/]?$",
        login_required(views.PulsarDetailView.as_view()),
        name="pulsar_detail",
    ),
    re_path(
        r"^search/(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)$",
        login_required(views.SearchDetailView.as_view()),
        name="pulsar_detail_search",
    ),
    re_path(
        r"^(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)/(?P<utc>\d{4}-\d{2}-\d{2}-[0-2]{1}\d{1}:[0-6]{1}\d{1}:[0-6]{1}\d{1})/(?P<beam>\d+)/$",
        login_required(views.ObservationDetailView.as_view()),
        name="obs_detail",
    ),
]
