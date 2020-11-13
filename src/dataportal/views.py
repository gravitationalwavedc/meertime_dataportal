from datetime import datetime

from django.shortcuts import get_object_or_404
from django.views import generic
from django.conf import settings
from django.db.models import Sum, Count, ExpressionWrapper, Max, Min, DurationField
import json


from .models import Observations, Pulsars, Proposals, Ephemerides, Utcs
from .plots import pulsar_summary_plot

from .logic import get_trapum_filters, get_meertime_filters

from sentry_sdk import last_event_id
from django.shortcuts import render


def handler500(request):
    if settings.ENABLE_SENTRY_DSN:
        return render(request, "500.html", {"sentry_event_id": last_event_id(), "sentry_dsn": settings.SENTRY_DSN,})
    else:
        return render(request, "500.html", {})


class SessionView(generic.ListView):
    """
    Display observations in an observing session
    """

    context_object_name = "obs_list"
    template_name = "dataportal/session.html"

    def get_queryset(self):
        return Observations.get_last_session_by_gap()


class IndexBaseView(generic.ListView):
    """
    Base view for main table views.
    """

    context_object_name = "per_pulsar_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meertime_filter = get_meertime_filters()
        context["projects"] = Proposals.objects.filter(**meertime_filter)
        context["project_id"] = self.request.GET.get("project_id")
        context["band"] = self.request.GET.get("band")
        qs = context["per_pulsar_list"]
        context["totals"] = qs.aggregate(global_tint_h=Sum("total_tint_h"), global_nobs=Sum("nobs"))
        context["totals"]["global_npsr"] = qs.count()
        return context


class FoldView(IndexBaseView):
    """
    Display pulsars and the latest meertime observation data.
    """

    template_name = "dataportal/index.html"

    def get_queryset(self):
        return Pulsars.get_observations(
            mode="observations", proposal=self.request.GET.get("project_id"), band=self.request.GET.get("band")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # page title
        context["title"] = "folded observations"
        return context


class TrapumView(IndexBaseView):
    """
    Display pulsars and the latest trapum observation data.
    """

    template_name = "dataportal/trapum.html"

    def get_queryset(self):
        return Pulsars.get_observations(
            mode="observations",
            proposal=self.request.GET.get("project_id"),
            band=self.request.GET.get("band"),
            get_proposal_filters=get_trapum_filters,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trapum_filters = get_trapum_filters()
        context["projects"] = Proposals.objects.filter(**trapum_filters)
        # page title
        context["title"] = "trapum observations"
        return context


class SearchmodeView(IndexBaseView):
    """
    Display pulsars and the latest observation data.
    """

    template_name = "dataportal/searchmode.html"

    def get_queryset(self):
        return Pulsars.get_observations(mode="searchmode", proposal=self.request.GET.get("project_id"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # page title
        context["title"] = "searchmode observations"
        return context


class DetailView(generic.ListView):
    context_object_name = "obs_list"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.pulsar = get_object_or_404(Pulsars, jname=self.kwargs["psr"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add ephemeris to the context
        context["psr"] = self.kwargs["psr"]
        try:
            ephemeris = Ephemerides.objects.get(pulsar=self.pulsar)
        except Ephemerides.DoesNotExist:
            ephemeris = None
            updated = None
        if ephemeris:
            updated = ephemeris.updated_at
            ephemeris = json.loads(ephemeris.ephemeris)
        context["ephemeris"] = ephemeris
        context["updated"] = updated

        # Add a payload for kronos/meerwatch links
        context["kronos"] = settings.KRONOS_PAYLOAD

        return context


class PulsarDetailView(DetailView):
    """
    Display detail list of meertime observations for a single pulsar.
    """

    template_name = "dataportal/show_single_psr.html"

    def get_queryset(self):
        return self.pulsar.observations_detail_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add a summary plot to the context
        plot_qs = context["obs_list"].values_list("utc__utc_ts", "snr_spip", "length")
        # If no observations exist, the unpacking below will throw a value error
        try:
            [UTCs, snrs, length] = list(zip(*plot_qs))
        except ValueError:
            [UTCs, snrs, length] = [
                (),
                (),
                (),
            ]

        bokeh_js, bokeh_div = pulsar_summary_plot(UTCs, snrs, length)
        context["bokeh_js"] = bokeh_js
        context["bokeh_div"] = bokeh_div

        # get total size
        qs = context["obs_list"]
        context["total_size_estimate"] = qs.aggregate(total_size_estimate=Sum("estimated_size"))

        # get other aggregates
        annotations = {}
        context["totals"] = qs.annotate(**annotations).aggregate(
            tint=Sum("length"),
            nobs=Count("id"),
            project_count=Count("proposal", distinct=True),
            timespan=ExpressionWrapper(Max("utc__utc_ts") - Min("utc__utc_ts"), output_field=DurationField()),
        )

        context["title"] = context["psr"]

        return context


class TrapumDetailView(DetailView):
    """
    Display detail list of trapum observations for a single pulsar.
    """

    template_name = "dataportal/show_single_psr.html"

    def get_queryset(self):
        return self.pulsar.observations_detail_data(get_proposal_filters=get_trapum_filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add a summary plot to the context
        UTCs = context["obs_list"].values_list("utc__utc_ts", flat=True)
        snrs = context["obs_list"].values_list("snr_spip", flat=True)
        length = context["obs_list"].values_list("length", flat=True)
        bokeh_js, bokeh_div = pulsar_summary_plot(UTCs, snrs, length)
        context["bokeh_js"] = bokeh_js
        context["bokeh_div"] = bokeh_div

        # get total size
        qs = context["obs_list"]
        context["total_size_estimate"] = qs.aggregate(total_size_estimate=Sum("estimated_size"))

        # get other aggregates
        annotations = {}
        context["totals"] = qs.annotate(**annotations).aggregate(
            tint=Sum("length"),
            nobs=Count("id"),
            project_count=Count("proposal", distinct=True),
            timespan=ExpressionWrapper(Max("utc__utc_ts") - Min("utc__utc_ts"), output_field=DurationField()),
        )

        context["title"] = f'Trapum: {context["psr"]}'

        return context


class SearchDetailView(DetailView):
    """
    Display detail list of search mode observations for a single pulsar
    """

    template_name = "dataportal/show_single_psr_search.html"

    def get_queryset(self):
        return self.pulsar.searchmode_detail_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # page title
        context["title"] = context["psr"] + " searchmode"
        return context


class ObservationDetailView(generic.TemplateView):
    """
    Display details of a single observation
    """

    template_name = "dataportal/observation.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.beam = self.kwargs["beam"]
        self.pulsar = get_object_or_404(Pulsars, jname=self.kwargs["psr"])

        self.utc_str = self.kwargs["utc"]
        utc_ts = datetime.strptime(f"{self.utc_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
        utc = get_object_or_404(Utcs, utc_ts=utc_ts)

        self.observation = get_object_or_404(Observations, pulsar=self.pulsar, utc=utc, beam=self.beam)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["obs"] = self.observation

        # Add a payload for kronos/meerwatch links
        context["kronos"] = settings.KRONOS_PAYLOAD

        context["title"] = f"{self.pulsar}/{self.utc_str}/{self.beam}"

        return context
