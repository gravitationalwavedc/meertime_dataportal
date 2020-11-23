import graphene
from django.template.defaultfilters import filesizeformat
from graphene import relay
from graphql_relay import from_global_id, to_global_id
from .models import Pulsars, Proposals
from graphql_jwt.decorators import login_required


class ObservationNode(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    jname = graphene.String()
    last = graphene.DateTime()
    first = graphene.DateTime()
    proposal_short = graphene.String()
    timespan = graphene.String()
    nobs = graphene.Int()
    total_tint_h = graphene.Float()
    avg_snr_5min = graphene.Float()
    max_snr_5min = graphene.Float()
    latest_snr = graphene.Float()
    latest_tint_m = graphene.Float()

    def resolve_timespan(self, instance):
        return self["timespan"].days

    def resolve_total_tint_h(self, instance):
        return round(self["total_tint_h"], 1) if self["total_tint_h"] else None

    def resolve_avg_snr_5min(self, instance):
        return round(self["avg_snr_5min"], 1) if self["avg_snr_5min"] else None

    def resolve_max_snr_5min(self, instance):
        return round(self["max_snr_5min"], 1) if self["max_snr_5min"] else None

    def resolve_latest_snr(self, instance):
        return round(self["latest_snr"], 1) if self["latest_snr"] else None

    def resolve_latest_tint_m(self, instance):
        return round(self["latest_tint_m"], 1) if self["latest_tint_m"] else None


class ObservationConnection(relay.Connection):
    class Meta:
        node = ObservationNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum([edge.node["nobs"] for edge in self.edges])

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum([edge.node["total_tint_h"] for edge in self.edges]), 1)


class ObservationDetailNode(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    utc = graphene.String()
    proposal_short = graphene.String()
    length = graphene.Float()
    beam = graphene.Int()
    bw = graphene.Float()
    nchan = graphene.Int()
    band = graphene.String()
    nbin = graphene.Int()
    nant = graphene.Int()
    nant_eff = graphene.Int()
    dm_fold = graphene.Float()
    dm_pipe = graphene.Float()
    rm_pipe = graphene.Float()
    snr_spip = graphene.Float()
    snr_pipe = graphene.Float()
    estimated_size = graphene.Float()

    def resolve_snr_spip(self, instance):
        return round(self.snr_spip, 1) if self.snr_spip else None

    def resolve_snr_pipe(self, instance):
        return round(self.snr_pipe, 1) if self.snr_pipe else None

    def resolve_length(self, instance):
        return round(self.length / 60, 1) if self.length else None


class ObservationDetailConnection(relay.Connection):
    class Meta:
        node = ObservationDetailNode

    jname = graphene.String()
    total_observations = graphene.Int()
    total_observation_hours = graphene.Float()
    total_estimated_disk_space = graphene.String()
    total_projects = graphene.Int()
    total_timespan_days = graphene.Int()

    def resolve_jname(self, instance):
        return self.iterable[0].pulsar.jname

    def resolve_total_observations(self, instance):
        return len(self.edges)

    def resolve_total_observation_hours(self, instance):
        return round(sum([observation.length for observation in self.iterable]) / 3600, 1)

    def resolve_total_projects(self, instance):
        return len({observation.proposal_short for observation in self.iterable})

    def resolve_total_timespan_days(self, instance):
        max_utc = max([observation.utc.utc_ts for observation in self.iterable])
        min_utc = min([observation.utc.utc_ts for observation in self.iterable])
        duration = max_utc - min_utc
        # Add 1 day to the end result because the timespan should show the rounded up number of days
        return duration.days + 1 if duration else 0

    def resolve_total_estimated_disk_space(self, instance):
        return filesizeformat(
            sum([observation.estimated_size for observation in self.iterable if observation.estimated_size])
        )


class Query(graphene.ObjectType):
    relay_observations = relay.ConnectionField(
        ObservationConnection, mode=graphene.String(required=True), proposal=graphene.String(), band=graphene.String(),
    )
    relay_observation_details = relay.ConnectionField(
        ObservationDetailConnection, jname=graphene.String(required=True)
    )

    @login_required
    def resolve_relay_observations(self, info, **kwargs):

        if kwargs["proposal"] and kwargs["proposal"] != "All":
            proposal_id = Proposals.objects.filter(proposal_short=kwargs["proposal"]).first().id
            kwargs["proposal"] = proposal_id
        else:
            kwargs["proposal"] = None

        if kwargs["band"] == "All":
            kwargs["band"] = None

        return Pulsars.get_observations(**kwargs)

    def resolve_relay_observation_details(self, info, **kwargs):
        return [
            observation for observation in Pulsars.objects.get(jname=kwargs.get('jname')).observations_detail_data()
        ]
