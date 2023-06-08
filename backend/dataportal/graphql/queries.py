import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from dataportal.models import Pulsar, Observation, MainProject, Project, Ephemeris

DATETIME_FILTERS = ["exact", "isnull", "lt", "lte", "gt", "gte", "month", "year", "date"]
NUMERIC_FILTERS = ["exact", "lt", "lte", "gt", "gte"]

class Queries:
    pass


class PulsarNode(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ObservationNode(DjangoObjectType):
    class Meta:
        model = Observation
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class MainProjectNode(DjangoObjectType):
    class Meta:
        model = MainProject
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)

class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        fields = "__all__"
        filter_fields = "__all__"
        interfaces = (relay.Node,)

    embargoPeriod = graphene.Int()

    def resolve_embargoPeriod(self, info):
        return self.embargo_period.days

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class EphemerisNode(DjangoObjectType):
    class Meta:
        model = Ephemeris
        fields = "__all__"
        filter_fields = {
            "pulsar__id": ["exact"],
            "p0": NUMERIC_FILTERS,
            "dm": NUMERIC_FILTERS,
            "ephemeris_hash": ["exact"],
        }

        interfaces = (relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info)


class Query(graphene.ObjectType):
    # pulsar = relay.Node.Field(PulsarNode)
    Pulsar = graphene.Field(
        PulsarNode,
        name=graphene.String(required=True),
    )
    allPulsars = DjangoFilterConnectionField(PulsarNode, max_limit=10000)

    Observation = relay.Node.Field(ObservationNode)
    allObservations = DjangoFilterConnectionField(ObservationNode, max_limit=10000)

    mainproject = graphene.Field(
        MainProjectNode,
        name=graphene.String(required=True),
    )
    allMainprojects = DjangoFilterConnectionField(MainProjectNode, max_limit=10000)

    project = graphene.Field(
        ProjectNode,
        code=graphene.String(required=True),
    )
    allProjects = DjangoFilterConnectionField(ProjectNode, max_limit=10000)

    ephemeris = relay.Node.Field(EphemerisNode)
    allEphemeriss = DjangoFilterConnectionField(EphemerisNode, max_limit=10000)


