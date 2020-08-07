from django.urls import path, re_path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path("fold/", login_required(views.FoldView.as_view()), name="fold"),
    path("search/", login_required(views.SearchmodeView.as_view()), name="search"),
    path("flux-calibrations/", login_required(views.FoldView.as_view()), name="flux_calibrations"),
    re_path(
        r"^(?P<psr>[BJ][0-2][0-9]*[-+][0-9]*[a-zA-Z]*)$",
        login_required(views.DetailView.as_view()),
        name="pulsar_detail",
    ),
]
