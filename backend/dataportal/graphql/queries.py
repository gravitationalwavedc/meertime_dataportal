import graphene
from graphql_jwt.decorators import login_required

from . import (
    basebandings,
    calibrations,
    collections,
    ephemerides,
    filterbankings,
    foldings,
    instrumentconfigs,
    launches,
    observations,
    pipelineimages,
    pipelines,
    processingcollections,
    processings,
    projects,
    pulsaraliases,
    pulsars,
    pulsartargets,
    rfis,
    targets,
    telescopes,
    templates,
    toas,
)


class Queries:
    pass


class Query(
    basebandings.Query,
    calibrations.Query,
    collections.Query,
    ephemerides.Query,
    filterbankings.Query,
    foldings.Query,
    instrumentconfigs.Query,
    launches.Query,
    observations.Query,
    pipelineimages.Query,
    pipelines.Query,
    processingcollections.Query,
    processings.Query,
    projects.Query,
    pulsaraliases.Query,
    pulsars.Query,
    pulsartargets.Query,
    rfis.Query,
    targets.Query,
    telescopes.Query,
    templates.Query,
    toas.Query,
    graphene.ObjectType,
):
    pass
