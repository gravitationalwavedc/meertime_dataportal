import graphene
from graphql_jwt.decorators import permission_required

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
    pulsars,
    pulsartargets,
    sessions,
    targets,
    telescopes,
    templates,
    toas,
)


class Mutation(
    basebandings.Mutation,
    calibrations.Mutation,
    collections.Mutation,
    ephemerides.Mutation,
    foldings.Mutation,
    filterbankings.Mutation,
    instrumentconfigs.Mutation,
    launches.Mutation,
    observations.Mutation,
    pipelinefiles.Mutation,
    pipelineimages.Mutation,
    pipelines.Mutation,
    processingcollections.Mutation,
    processings.Mutation,
    programs.Mutation,
    projects.Mutation,
    pulsars.Mutation,
    pulsartargets.Mutation,
    sessions.Mutation,
    targets.Mutation,
    telescopes.Mutation,
    templates.Mutation,
    toas.Mutation,
    graphene.ObjectType,
):
    pass
