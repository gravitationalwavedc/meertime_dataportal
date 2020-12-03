from datetime import datetime

from django.shortcuts import get_object_or_404
from django.views import generic
from django.conf import settings
from django.db.models import Sum, Count, ExpressionWrapper, Max, Min, DurationField
import json


# from .models import Observations, Pulsars, Proposals, Ephemerides, Utcs, get_observations_summary
from .models import Pulsars
from .plots import pulsar_summary_plot

from .logic import get_meertime_filters

from sentry_sdk import last_event_id
from django.shortcuts import render


def handler500(request):
    if settings.ENABLE_SENTRY_DSN:
        return render(request, "500.html", {"sentry_event_id": last_event_id(), "sentry_dsn": settings.SENTRY_DSN,})
    else:
        return render(request, "500.html", {})


# class SessionView(generic.ListView):
#    """
#    Display observations in an observing session
#    """
#
#    context_object_name = "obs_list"
#    template_name = "dataportal/session.html"
#    page_title = "last meertime session"
#    detail_url_name = "pulsar_detail"
#    get_proposal_filters = get_meertime_filters
#
#    def get_queryset(cls):
#        return Observations.get_last_session_by_gap(get_proposal_filters=cls.get_proposal_filters)
#
#    def get_context_data(cls, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context["session_meta"] = get_observations_summary(context["obs_list"])
#        context["detail_url_name"] = cls.detail_url_name
#        context["title"] = cls.page_title
#        return context


# class IndexBaseView(generic.ListView):
#    """
#    Base view for main table views.
#    """
#
#    context_object_name = "per_pulsar_list"
#
#    def get_context_data(cls, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context["project_id"] = cls.request.GET.get("project_id")
#        context["band"] = cls.request.GET.get("band")
#        qs = context["per_pulsar_list"]
#        context["totals"] = qs.aggregate(global_tint_h=Sum("total_tint_h"), global_nobs=Sum("nobs"))
#        context["totals"]["global_npsr"] = qs.count()
#        return context


# class FoldView(IndexBaseView):
#    """
#    Display pulsars and the latest meertime observation data.
#    """
#
#    template_name = "dataportal/index.html"
#    page_title = "folded observations"
#    detail_url_name = "pulsar_detail"
#    get_proposal_filters = get_meertime_filters
#
#    def get_queryset(cls):
#        return Pulsars.get_observations(
#            mode="observations",
#            proposal=cls.request.GET.get("project_id"),
#            band=cls.request.GET.get("band"),
#            get_proposal_filters=cls.get_proposal_filters,
#        )
#
#    def get_context_data(cls, **kwargs):
#        context = super().get_context_data(**kwargs)
#        proposal_filter = cls.get_proposal_filters()
#        context["projects"] = Proposals.objects.filter(**proposal_filter)
#        # page title
#        context["title"] = cls.page_title
#        context["detail_url_name"] = cls.detail_url_name
#        return context


# class SearchmodeView(IndexBaseView):
#    """
#    Display pulsars and the latest observation data.
#    """
#
#    template_name = "dataportal/searchmode.html"
#    get_proposal_filters = get_meertime_filters
#    detail_url_name = "pulsar_detail_search"
#    page_title = "searchmode observations"
#
#    def get_queryset(cls):
#        return Pulsars.get_observations(
#            mode="searchmode",
#            proposal=cls.request.GET.get("project_id"),
#            get_proposal_filters=cls.get_proposal_filters,
#        )
#
#    def get_context_data(cls, **kwargs):
#        context = super().get_context_data(**kwargs)
#        # page title
#        context["title"] = cls.page_title
#        context["detail_url_name"] = cls.detail_url_name
#        return context


class DetailView(generic.ListView):
    context_object_name = "obs_list"

    def setup(cls, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        cls.pulsar = get_object_or_404(Pulsars, jname=cls.kwargs["psr"])

    def get_context_data(cls, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add ephemeris to the context
        context["psr"] = cls.kwargs["psr"]
        # try:
        #    ephemeris = Ephemerides.objects.get(pulsar=cls.pulsar)
        # except Ephemerides.DoesNotExist:
        #    ephemeris = None
        #    updated = None
        # if ephemeris:
        #    updated = ephemeris.updated_at
        #    ephemeris = json.loads(ephemeris.ephemeris)
        context["ephemeris"] = None  # ephemeris
        context["updated"] = None  # updated

        # Add a payload for kronos/meerwatch links
        context["kronos"] = settings.KRONOS_PAYLOAD

        return context


class PulsarDetailView(DetailView):
    """
    Display detail list of meertime observations for a single pulsar.
    """

    template_name = "dataportal/show_single_psr.html"
    get_proposal_filters = get_meertime_filters

    def get_queryset(cls):
        return cls.pulsar.get_observations_detail_data(get_proposal_filters=cls.get_proposal_filters)

    def get_context_data(cls, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add a summary plot to the context
        # plot_qs = context["obs_list"].values_list("utc__utc_ts", "snr_spip", "length")
        # If no observations exist, the unpacking below will throw a value error
        # try:
        #    [UTCs, snrs, length] = list(zip(*plot_qs))
        # except ValueError:
        #    [UTCs, snrs, length] = [
        #        (),
        #        (),
        #        (),
        #    ]

        # bokeh_js, bokeh_div = pulsar_summary_plot(UTCs, snrs, length)
        context["bokeh_js"] = ""  # bokeh_js
        context["bokeh_div"] = ""  # bokeh_div

        # get total size
        qs = context["obs_list"]
        context["total_size_estimate"] = 0  # qs.aggregate(total_size_estimate=Sum("estimated_size"))

        # get other aggregates
        annotations = {}
        # context["totals"] = qs.annotate(**annotations).aggregate(
        #    tint=Sum("length"),
        #    nobs=Count("id"),
        #    project_count=Count("proposal", distinct=True),
        #    timespan=ExpressionWrapper(Max("utc__utc_ts") - Min("utc__utc_ts"), output_field=DurationField()),
        # )

        context["title"] = context["psr"]

        return context


# class SearchDetailView(DetailView):
#    """
#    Display detail list of search mode observations for a single pulsar
#    """
#
#    template_name = "dataportal/show_single_psr_search.html"
#    page_title_prefix = ""
#    get_proposal_filters = get_meertime_filters
#
#    def get_queryset(cls):
#        return cls.pulsar.searchmode_detail_data(get_proposal_filters=cls.get_proposal_filters)
#
#    def get_context_data(cls, **kwargs):
#        context = super().get_context_data(**kwargs)
#        # page title
#        context["title"] = f'{cls.page_title_prefix} {context["psr"]} searchmode'
#        return context


# class ObservationDetailView(generic.TemplateView):
#    """
#    Display details of a single observation
#    """
#
#    template_name = "dataportal/observation.html"
#
#    def setup(cls, request, *args, **kwargs):
#        super().setup(request, *args, **kwargs)
#
#        cls.beam = cls.kwargs["beam"]
#        cls.pulsar = get_object_or_404(Pulsars, jname=cls.kwargs["psr"])
#
#        cls.utc_str = cls.kwargs["utc"]
#        utc_ts = datetime.strptime(f"{cls.utc_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
#        utc = get_object_or_404(Utcs, utc_ts=utc_ts)
#
#        cls.observation = get_object_or_404(Observations, pulsar=cls.pulsar, utc=utc, beam=cls.beam)
#
#    def get_context_data(cls, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context["obs"] = cls.observation
#        # Add a payload for kronos/meerwatch links
#        context["kronos"] = settings.KRONOS_PAYLOAD
#        context["title"] = f"{cls.pulsar}/{cls.utc_str}/{cls.beam}"
#
#        return context
