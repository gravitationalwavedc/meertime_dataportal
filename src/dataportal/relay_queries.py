import graphene
from graphene import relay
from graphql_relay import from_global_id, to_global_id
from .models import Pulsars, Proposals
from graphql_jwt.decorators import login_required


class FoldObservationNode(graphene.ObjectType):
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


class FoldObservationConnection(relay.Connection):
    class Meta:
        node = FoldObservationNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum([edge.node["nobs"] for edge in self.edges])

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum([edge.node["total_tint_h"] for edge in self.edges]), 1)


class Query(graphene.ObjectType):
    fold_observations = relay.ConnectionField(
        FoldObservationConnection,
        mode=graphene.String(required=True),
        proposal=graphene.String(),
        band=graphene.String(),
    )

    @login_required
    def resolve_fold_observations(self, info, **kwargs):

        if kwargs["proposal"] and kwargs["proposal"] != 'All':
            proposal_id = Proposals.objects.filter(proposal_short=kwargs["proposal"]).first().id
            kwargs["proposal"] = proposal_id
        else:
            kwargs["proposal"] = None

        if kwargs["band"] == 'All':
            kwargs["band"] = None

        return Pulsars.get_observations(**kwargs)
