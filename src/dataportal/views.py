from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.http import HttpResponse
from django.views import generic

from .models import Observations, Pulsars

from django.template.defaulttags import register

from importlib import import_module


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def get_raw_query(table, proposal_filter):
    raw_query = (
        "SELECT o.id, o.pulsar_id, o.beam, "
        + "o.utc_id, p.Jname, x.nobs, x.maxu as last, x.minu as first, "
        + "TIMESTAMPDIFF(DAY,x.minu, x.maxu)+1 as timespan, "
        + "avg_snr_5min, max_snr_5min, total_tint_h, "
        + "proposal_short as project, o.snr_spip as latest_snr, "
        + "o.length/60 as latest_tint_m "
        + "FROM (SELECT COUNT(*) as nobs, MAX(utc_ts) as maxu, "
        + "MIN(utc_ts) as minu, pulsar_id, MAX(utc_id) as last, "
        + "AVG(snr_pipe/SQRT(length)*sqrt(300)) AS avg_snr_5min, "
        + "MAX(snr_pipe/SQRT(length)*sqrt(300)) AS max_snr_5min, "
        + "SUM(length)/60/60 AS total_tint_h FROM "
        + table
        + " JOIN UTCs ON UTCs.id = "
        + table
        + ".utc_id JOIN Proposals ON "
        + table
        + ".proposal_id = Proposals.id "
        + proposal_filter
        + "GROUP BY pulsar_id ORDER BY last DESC) as x JOIN "
        + table
        + " AS o ON o.utc_id = x.last AND "
        + "o.pulsar_id = x.pulsar_id JOIN UTCs AS u ON o.utc_id = u.id "
        + "JOIN Pulsars AS p ON p.id = o.pulsar_id JOIN Proposals AS "
        + "prop ON o.proposal_id = prop.id"
    )

    return raw_query


class IndexView(generic.ListView):
    """
    This view uses a raw query as I didn't find an acceptable way to do a
    greatest-n-per-group type of query in django which was efficient and
    scalable. While the query seems complicated, it is quite a standard query
    for retrieving not only the aggregate values when grouping by, but also the
    latest entry per group. The grouping is on pulsar, but the users are also
    very interested in getting some of the metadata for the latest observation
    for every pulsar in this view.
    """

    template_name = "dataportal/index.html"
    context_object_name = "per_pulsar_list"
    order_by = "last"

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, self.request.path))
        return super(IndexView, self).get(*args, **kwargs)

    def get_queryset(self):
        proposal_filter = "WHERE proposal LIKE 'SCI%%' "
        raw_params = []
        project_id = self.request.GET.get("project_id")
        if project_id:
            proposal_filter = "WHERE proposal_id = %s"
            raw_params = [project_id]

        table = self.request.GET.get("table", "Observations")
        raw_query = get_raw_query(table, proposal_filter)

        module = import_module("dataportal.models")
        class_ = getattr(module, table)

        psr_list = class_.objects.raw(raw_query, raw_params)
        return psr_list

    def get_context_data(self, **kwargs):
        from .models import Proposals

        context = super().get_context_data(**kwargs)
        context["projects"] = Proposals.objects.filter(proposal__contains="SCI")
        context["project_id"] = self.request.GET.get("project_id")
        return context


class DetailView(generic.ListView):

    template_name = "dataportal/show_single_psr.html"
    context_object_name = "obs_list"

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            print(self.request.path)
            return redirect("%s?next=%s" % (settings.LOGIN_URL, self.request.path))
        return super(DetailView, self).get(*args, **kwargs)

    def get_queryset(self):
        from .models import Pulsars

        pulsar = get_object_or_404(Pulsars, jname=self.kwargs["psr"])
        return (
            Observations.objects.filter(pulsar=pulsar)
            .values(
                "utc__utc",
                "proposal__proposal_short",
                "length",
                "beam",
                "bw",
                "frequency",
                "nchan",
                "nbin",
                "nant",
                "dm_fold",
                "dm_pipe",
                "rm_pipe",
                "snr_spip",
                "snr_pipe",
            )
            .order_by("-utc__utc_ts")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["psr"] = self.kwargs["psr"]
        return context
