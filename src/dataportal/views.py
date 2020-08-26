from django.shortcuts import get_object_or_404
from django.views import generic
from meertime.settings import SENTRY_DSN


from .models import Pulsars, Proposals

from sentry_sdk import last_event_id
from django.shortcuts import render


def handler500(request):
    return render(request, "500.html", {"sentry_event_id": last_event_id(), "sentry_dsn": SENTRY_DSN,})


class IndexBaseView(generic.ListView):
    """
    Base view for main table views.
    """

    context_object_name = "per_pulsar_list"
    order_by = "last"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = Proposals.objects.filter(proposal__contains="SCI")
        context["project_id"] = self.request.GET.get("project_id")
        return context


class FoldView(IndexBaseView):
    """
    Display pulsars and the latest observation data.
    """

    template_name = "dataportal/index.html"

    def get_queryset(self):
        return Pulsars.get_observations(mode="observations", proposal_id=self.request.GET.get("project_id"))


class SearchmodeView(IndexBaseView):
    """
    Display pulsars and the latest observation data.
    """

    template_name = "dataportal/searchmode.html"

    def get_queryset(self):
        return Pulsars.get_observations(mode="searchmode", proposal_id=self.request.GET.get("project_id"))


class DetailView(generic.ListView):
    """
    Display detail list of observations for a single pulsar.
    """

    template_name = "dataportal/show_single_psr.html"
    context_object_name = "obs_list"

    def get_queryset(self):
        pulsar = get_object_or_404(Pulsars, jname=self.kwargs["psr"])
        return pulsar.observations_detail_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["psr"] = self.kwargs["psr"]
        return context


class SearchDetailView(generic.ListView):
    """
    Display detail list of search mode observations for a single pulsar
    """

    template_name = "dataportal/show_single_psr_search.html"
    context_object_name = "obs_list"

    def get_queryset(self):
        pulsar = get_object_or_404(Pulsars, jname=self.kwargs["psr"])
        return pulsar.searchmode_detail_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["psr"] = self.kwargs["psr"]
        return context
