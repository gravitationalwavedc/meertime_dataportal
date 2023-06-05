import graphene
from graphql_jwt.decorators import login_required
from graphene_django import DjangoObjectType

from dataportal.models import Pulsar

from . import (
    pulsar,
    # Ephemeris,
    # Template,
    # Calibration,
    # Telescope,
    # MainProject,
    # Session,
    # Observation,
    # PipelineRun,
    # PipelineImage,
    # PipelineFile,
    # Toa,
)


class Queries:
    pass


class PulsarType(DjangoObjectType):
    class Meta:
        model = Pulsar
        fields = "__all__"
        filter_fields = "__all__"

class Query(
    # pulsar.Query,
    # Ephemeris.Query,
    # Template.Query,
    # Calibration.Query,
    # Telescope.Query,
    # MainProject.Query,
    # Session.Query,
    # Observation.Query,
    # PipelineRun.Query,
    # PipelineImage.Query,
    # PipelineFile.Query,
    # Toa.Query,
    graphene.ObjectType,
):
    pulsars = graphene.List(PulsarType)

    def resolve_pulsars(self, info, **kwargs):
        return Pulsar.objects.all()
