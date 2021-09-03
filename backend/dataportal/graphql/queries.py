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
    pipelinefiles,
    pipelineimages,
    pipelines,
    processingcollections,
    processings,
    programs,
    projects,
    pulsaraliases,
    pulsars,
    pulsartargets,
    rfis,
    sessions,
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
    pipelinefiles.Query,
    pipelineimages.Query,
    pipelines.Query,
    processingcollections.Query,
    processings.Query,
    programs.Query,
    projects.Query,
    pulsaraliases.Query,
    pulsars.Query,
    pulsartargets.Query,
    rfis.Query,
    sessions.Query,
    targets.Query,
    telescopes.Query,
    templates.Query,
    toas.Query,
    graphene.ObjectType,
):
    pass
