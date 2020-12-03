from django.urls import path, re_path
from django.contrib.auth.decorators import login_required

from .logic import get_trapum_filters, get_meertime_filters

from . import views

urlpatterns = [
    #    path("", login_required(views.FoldView.as_view(get_proposal_filters=get_meertime_filters,)), name="fold"),
    #    path(
    #        "trapum/",
    #        login_required(
    #            views.FoldView.as_view(
    #                get_proposal_filters=get_trapum_filters,
    #                page_title="trapum observations",
    #                detail_url_name="pulsar_detail_trapum",
    #            )
    #        ),
    #        name="trapum",
    #    ),
    #    path(
    #        "session/",
    #        login_required(views.SessionView.as_view(get_proposal_filters=get_meertime_filters)),
    #        name="session",
    #    ),
    #    path(
    #        "trapum/session/",
    #        login_required(
    #            views.SessionView.as_view(
    #                get_proposal_filters=get_trapum_filters,
    #                page_title="last trapum session",
    #                detail_url_name="pulsar_detail_trapum",
    #            )
    #        ),
    #        name="trapum_session",
    #    ),
    #    path(
    #        "trapum/search/",
    #        login_required(
    #            views.SearchmodeView.as_view(
    #                get_proposal_filters=get_trapum_filters,
    #                page_title="trapum searchmode observations",
    #                detail_url_name="pulsar_detail_search_trapum",
    #            )
    #        ),
    #        name="trapum_search",
    #    ),
    #    path(
    #        "search/",
    #        login_required(
    #            views.SearchmodeView.as_view(
    #                get_proposal_filters=get_meertime_filters,
    #                page_title="searchmode observations",
    #                detail_url_name="pulsar_detail_search",
    #            )
    #        ),
    #        name="search",
    #    ),
    #    path("fluxcal/", login_required(views.FoldView.as_view()), name="fluxcal"),
    re_path(
        r"^(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)[/]?$",
        login_required(views.PulsarDetailView.as_view(get_proposal_filters=get_meertime_filters)),
        name="pulsar_detail",
    ),
    #    re_path(
    #        r"^trapum/(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)$",
    #        login_required(views.PulsarDetailView.as_view(get_proposal_filters=get_trapum_filters)),
    #        name="pulsar_detail_trapum",
    #    ),
    #    re_path(
    #        r"^search/(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)$",
    #        login_required(views.SearchDetailView.as_view(get_proposal_filters=get_meertime_filters)),
    #        name="pulsar_detail_search",
    #    ),
    #    re_path(
    #        r"^trapum/search/(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)$",
    #        login_required(
    #            views.SearchDetailView.as_view(get_proposal_filters=get_trapum_filters, page_title_prefix="trapum")
    #        ),
    #        name="pulsar_detail_search_trapum",
    #    ),
    #    re_path(
    #        r"^(?P<psr>[BJ][0-2]\d*[-+]+\d*[a-zA-Z]*)/(?P<utc>\d{4}-\d{2}-\d{2}-[0-2]{1}\d{1}:[0-6]{1}\d{1}:[0-6]{1}\d{1})/(?P<beam>\d+)/$",
    #        login_required(views.ObservationDetailView.as_view()),
    #        name="obs_detail",
    #    ),
]
