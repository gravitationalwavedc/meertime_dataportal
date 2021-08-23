import graphene
import json
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from web_cache.models import FoldPulsar, SearchmodePulsar, FoldPulsarDetail, SearchmodePulsarDetail
from graphql_jwt.decorators import login_required


class FoldPulsarNode(DjangoObjectType):
    class Meta:
        model = FoldPulsar
        interfaces = (relay.Node,)


class FoldPulsarDetailNode(DjangoObjectType):
    class Meta:
        model = FoldPulsarDetail
        interfaces = (relay.Node,)
        exclude = ["ephemeris"]

    ephemeris = graphene.String()

    def resolve_ephemeris(self, instance):
        """Make sure that graphql outputs a valid json string that can be used in JSON.parse"""
        return json.dumps(self.ephemeris)


class SearchmodePulsarNode(DjangoObjectType):
    class Meta:
        model = SearchmodePulsar
        interfaces = (relay.Node,)


class SearchmodePulsarDetailNode(DjangoObjectType):
    class Meta:
        model = SearchmodePulsarDetail
        interfaces = (relay.Node,)


class FoldPulsarConnection(relay.Connection):
    class Meta:
        node = FoldPulsarNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum([edge.node.number_of_observations for edge in self.edges if edge.node.number_of_observations])

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum([edge.node.total_integration_hours for edge in self.edges]), 1)


class FoldPulsarDetailConnection(relay.Connection):
    class Meta:
        node = FoldPulsarDetailNode

    total_observations = graphene.Int()
    total_observation_hours = graphene.Int()
    total_estimated_disk_space = graphene.String()
    total_projects = graphene.Int()
    total_timespan_days = graphene.Int()
    max_plot_length = graphene.Int()
    min_plot_length = graphene.Int()

    def resolve_total_observations(self, instance):
        return len(self.edges)

    def resolve_total_observation_hours(self, instance):
        return round(sum([observation.length for observation in self.iterable]) / 3600, 1)

    def resolve_total_projects(self, instance):
        return len({observation.project for observation in self.iterable})

    def resolve_total_timespan_days(self, instance):
        max_utc = max([observation.utc for observation in self.iterable]) if self.iterable else 0
        min_utc = min([observation.utc for observation in self.iterable]) if self.iterable else 0
        duration = max_utc - min_utc
        # Add 1 day to the end result because the timespan should show the rounded up number of days
        return duration.days + 1 if duration else 0

    def resolve_total_estimated_disk_space(self, instance):
        return '0 mb'
        # return filesizeformat(
        #     sum([observation.estimated_size for observation in self.iterable if observation.estimated_size])
        # )

    def resolve_max_plot_length(self, instance):
        return FoldPulsarDetail.objects.order_by('length').last().length

    def resolve_min_plot_length(self, instance):
        return FoldPulsarDetail.objects.order_by('-length').last().length


class SearchmodePulsarConnections(relay.Connection):
    class Meta:
        node = SearchmodePulsarNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum([edge.node.number_of_observations for edge in self.edges if edge.node.number_of_observations])

    def resolve_total_pulsars(self, instance):
        return len(self.edges)


class SearchmodePulsarDetailConnection(relay.Connection):
    class Meta:
        node = SearchmodePulsarDetailNode

    total_observations = graphene.Int()
    total_projects = graphene.Int()
    total_timespan_days = graphene.Int()

    def resolve_total_observations(self, instance):
        return len(self.edges)

    def resolve_total_projects(self, instance):
        return len({observation.project for observation in self.iterable})

    def resolve_total_timespan_days(self, instance):
        max_utc = max([observation.utc for observation in self.iterable])
        min_utc = min([observation.utc for observation in self.iterable])
        duration = max_utc - min_utc
        # Add 1 day to the end result because the timespan should show the rounded up number of days
        return duration.days + 1 if duration else 0


class Query(ObjectType):
    fold_observations = relay.ConnectionField(
        FoldPulsarConnection, main_project=graphene.String(), project=graphene.String(), band=graphene.String()
    )

    fold_observation_details = relay.ConnectionField(
        FoldPulsarDetailConnection,
        jname=graphene.String(required=True),
        main_project=graphene.String(),
        project=graphene.String(),
        utc=graphene.String(),
        beam=graphene.Int(),
    )

    searchmode_observations = relay.ConnectionField(
        SearchmodePulsarConnections, main_project=graphene.String(), project=graphene.String(), band=graphene.String()
    )

    searchmode_observation_details = relay.ConnectionField(
        SearchmodePulsarDetailConnection,
        jname=graphene.String(required=True),
        main_project=graphene.String(),
        project=graphene.String(),
    )

    @login_required
    def resolve_fold_observations(self, info, **kwargs):
        return FoldPulsar.get_query(**kwargs)

    @login_required
    def resolve_fold_observation_details(self, info, **kwargs):
        return FoldPulsarDetail.get_query(**kwargs)

    @login_required
    def resolve_searchmode_observations(self, info, **kwargs):
        return SearchmodePulsar.get_query(**kwargs)

    @login_required
    def resolve_searchmode_observation_details(self, info, **kwargs):
        return SearchmodePulsarDetail.get_query(**kwargs)
