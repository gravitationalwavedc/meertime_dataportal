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
    pipelineimages,
    pipelines,
    processingcollections,
    processings,
    projects,
    pulsars,
    pulsartargets,
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
    pipelineimages.Mutation,
    pipelines.Mutation,
    processingcollections.Mutation,
    processings.Mutation,
    projects.Mutation,
    pulsars.Mutation,
    pulsartargets.Mutation,
    targets.Mutation,
    telescopes.Mutation,
    templates.Mutation,
    toas.Mutation,
    graphene.ObjectType,
):
    pass
