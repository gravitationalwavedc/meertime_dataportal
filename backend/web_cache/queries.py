from datetime import datetime

import graphene
import json

import pytz
from django.contrib.auth import get_user_model
from graphene import relay, ObjectType
from django.template.defaultfilters import filesizeformat
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from web_cache.models import (
    FoldPulsar,
    FoldPulsarFile,
    SearchmodePulsar,
    FoldPulsarDetail,
    FoldDetailImage,
    SearchmodePulsarDetail,
    SessionDisplay,
    SessionPulsar,
)

from utils import constants

User = get_user_model()


class FoldDetailImageNode(DjangoObjectType):
    class Meta:
        model = FoldDetailImage
        interfaces = (relay.Node,)

    # These attributes map to FoldDetailImage properties
    process = graphene.String()
    resolution = graphene.String()
    plot_type = graphene.String()
    generic_plot_type = graphene.String()


class FoldPulsarFileNode(DjangoObjectType):
    class Meta:
        model = FoldPulsarFile
        interfaces = (relay.Node,)
        fields = ("image_type", "url", "project", "file_type")

    # These attributes map to FoldPulsarFile properties
    project = graphene.String()
    file_type = graphene.String()


class FoldPulsarNode(DjangoObjectType):
    class Meta:
        model = FoldPulsar
        interfaces = (relay.Node,)

    total_integration_hours = graphene.Float()
    last_sn_raw = graphene.Float()
    highest_sn_raw = graphene.Float()
    lowest_sn_raw = graphene.Float()
    avg_sn_pipe = graphene.Float()
    max_sn_pipe = graphene.Float()

    def resolve_last_integration_minutes(self, instance):
        return round(self.last_integration_minutes, 1)


class FoldPulsarDetailNode(DjangoObjectType):
    class Meta:
        model = FoldPulsarDetail
        interfaces = (relay.Node,)
        exclude = ["ephemeris"]

    ephemeris = graphene.String()
    band = graphene.String()
    jname = graphene.String()
    restricted = graphene.Boolean()

    # These are stored as decimals which are converted to strings as defaultself.
    # Strings break the frontend sorting.
    bw = graphene.Float()
    dm_fold = graphene.Float()
    dm_meerpipe = graphene.Float()
    rm_meerpipe = graphene.Float()
    sn_backend = graphene.Float()
    sn_meerpipe = graphene.Float()
    flux = graphene.Float()
    tsubint = graphene.Float()
    frequency = graphene.Float()

    def resolve_ephemeris(self, instance):
        """Make sure that graphql outputs a valid json string that can be used in JSON.parse"""
        return json.dumps(self.ephemeris)

    def resolve_band(self, instance):
        """Band should use the display name. This also stops graphene from replacing the - with an _."""
        return self.get_band_display()

    def resolve_length(self, instance):
        return round(self.length / 60)

    def resolve_restricted(self, info):
        # by default, we assume that the user is restricted
        restricted = True
        try:
            # checking whether the user is restricted or not
            restricted = (
                info.context.user.role.casefold()
                == constants.UserRole.RESTRICTED.value.casefold()
            )

            if restricted:
                # if the user is restricted, then we check this Pulsar's embargo date
                return self.embargo_end_date >= datetime.now(tz=pytz.UTC)
            else:
                # if the user is not restricted, we return False (restricted)
                return restricted
        except Exception:
            # default fallback to restricted (True)
            return restricted


class SearchmodePulsarNode(DjangoObjectType):
    class Meta:
        model = SearchmodePulsar
        interfaces = (relay.Node,)


class SearchmodePulsarDetailNode(DjangoObjectType):
    class Meta:
        model = SearchmodePulsarDetail
        interfaces = (relay.Node,)

    frequency = graphene.Float()
    dm = graphene.Float()
    tsamp = graphene.Float()

    def resolve_ra(self, instance):
        return self.ra[:-5]

    def resolve_dec(self, instance):
        return self.dec[:-5]

    def resolve_length(self, instance):
        return round(self.length / 60)


class SessionPulsarNode(DjangoObjectType):
    class Meta:
        model = SessionPulsar
        interfaces = (relay.Node,)

    jname = graphene.String()
    pulsar_type = graphene.String()
    frequency = graphene.Float()

    def resolve_frequency(self, instance):
        return round(self.frequency, 1)

    def resolve_integrations(self, instance):
        return round(self.integrations)


class FoldPulsarConnection(relay.Connection):
    class Meta:
        node = FoldPulsarNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()
    total_observation_time = graphene.Int()
    total_project_time = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum(
            edge.node.number_of_observations
            for edge in self.edges
            if edge.node.number_of_observations
        )

    def resolve_total_pulsars(self, instance):
        return len(self.edges)

    def resolve_total_observation_time(self, instance):
        return round(sum(edge.node.total_integration_hours for edge in self.edges), 1)

    def resolve_total_project_time(self, instance):
        # Too slow n(2)
        total_seconds = sum(
            fold.length
            for fold in FoldPulsarDetail.objects.filter(
                project=self.edges[0].node.project
            )
        )
        return int(total_seconds / 60 / 60)


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
    description = graphene.String()
    ephemeris_link = graphene.String()
    toas_link = graphene.String()

    def resolve_toas_link(self, instance):
        return (
            self.iterable.first()
            .fold_pulsar.foldpulsardetail_set.first()
            .toas_download_link
        )

    def resolve_ephemeris_link(self, instance):
        return (
            self.iterable.first()
            .fold_pulsar.foldpulsardetail_set.first()
            .ephemeris_download_link
        )

    def resolve_description(self, instance):
        return self.iterable.first().fold_pulsar.comment

    def resolve_total_observations(self, instance):
        return len(self.edges)

    def resolve_total_observation_hours(self, instance):
        return sum(float(observation.length) for observation in self.iterable) / 3600

    def resolve_total_projects(self, instance):
        return len({observation.project for observation in self.iterable})

    def resolve_total_timespan_days(self, instance):
        if self.iterable:
            max_utc = max(observation.utc for observation in self.iterable)
            min_utc = min(observation.utc for observation in self.iterable)
            duration = max_utc - min_utc
            # Add 1 day to the end result because the timespan should show the rounded up number of days
            return duration.days + 1
        else:
            return 0

    def resolve_total_estimated_disk_space(self, instance):
        total_bytes = sum(observation.estimated_size for observation in self.iterable)
        return filesizeformat(total_bytes)

    def resolve_max_plot_length(self, instance):
        return FoldPulsarDetail.objects.order_by("length").last().length

    def resolve_min_plot_length(self, instance):
        return FoldPulsarDetail.objects.order_by("-length").last().length


class SearchmodePulsarConnections(relay.Connection):
    class Meta:
        node = SearchmodePulsarNode

    total_observations = graphene.Int()
    total_pulsars = graphene.Int()

    def resolve_total_observations(self, instance):
        return sum(
            edge.node.number_of_observations
            for edge in self.edges
            if edge.node.number_of_observations
        )

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
        max_utc = max(observation.utc for observation in self.iterable)
        min_utc = min(observation.utc for observation in self.iterable)
        duration = max_utc - min_utc
        # Add 1 day to the end result because the timespan should show the rounded up number of days
        return duration.days + 1 if duration else 0


class SessionPulsarConnection(relay.Connection):
    class Meta:
        node = SessionPulsarNode

    start = graphene.DateTime()
    end = graphene.DateTime()
    number_of_observations = graphene.Int()
    number_of_pulsars = graphene.Int()

    def resolve_start(self, instance):
        return self.iterable.first().session_display.start if self.iterable else None

    def resolve_end(self, instance):
        return self.iterable.first().session_display.end if self.iterable else None

    def resolve_number_of_observations(self, instance):
        session_display = self.iterable.first().session_display
        total = 0
        for pulsar in self.iterable:
            if pulsar.fold_pulsar:
                total += pulsar.fold_pulsar.foldpulsardetail_set.filter(
                    utc__range=(session_display.start, session_display.end)
                ).count()
            if pulsar.search_pulsar:
                total += pulsar.search_pulsar.searchmodepulsardetail_set.filter(
                    utc__range=(session_display.start, session_display.end)
                ).count()
        return total

    def resolve_number_of_pulsars(self, instance):
        return len(self.edges)


class SessionListNode(DjangoObjectType):
    class Meta:
        model = SessionDisplay
        interfaces = (relay.Node,)

    session_pulsars = relay.ConnectionField(
        SessionPulsarConnection, project=graphene.String()
    )

    def resolve_frequency(self, instance):
        return round(self.frequency, 1) if self.frequency else None

    def resolve_total_integration(self, instance):
        return self.total_integration

    def resolve_session_pulsars(self, instance, **kwargs):
        return self.get_session_pulsars(**kwargs)


class SessionListConnection(relay.Connection):
    class Meta:
        node = SessionListNode


class Query(ObjectType):
    fold_pulsar = graphene.Field(FoldPulsarNode, jname=graphene.String(required=True))

    fold_observations = relay.ConnectionField(
        FoldPulsarConnection,
        main_project=graphene.String(),
        project=graphene.String(),
        band=graphene.String(),
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
        SearchmodePulsarConnections,
        main_project=graphene.String(),
        project=graphene.String(),
        band=graphene.String(),
    )

    searchmode_observation_details = relay.ConnectionField(
        SearchmodePulsarDetailConnection,
        jname=graphene.String(required=True),
        main_project=graphene.String(),
        project=graphene.String(),
    )

    session_display = graphene.Field(
        SessionListNode,
        start=graphene.String(),
        end=graphene.String(),
        utc=graphene.String(),
        project=graphene.String(),
    )

    session_list = relay.ConnectionField(SessionListConnection)

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

    @login_required
    def resolve_session_list(self, info, **kwargs):
        return SessionDisplay.get_query(**kwargs)

    @login_required
    def resolve_session_display(self, info, **kwargs):
        return SessionDisplay.get_query_instance(**kwargs)

    @login_required
    def resolve_fold_pulsar(self, info, **kwargs):
        return FoldPulsar.objects.get(jname=kwargs.get("jname"))
