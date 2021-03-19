import graphene
from graphql_jwt.decorators import permission_required

from . import (
    calibrations,
    ephemerides,
    foldings,
    instrumentconfigs,
    launches,
    observations,
    pipelineimages,
    pipelines,
    processings,
    projects,
    pulsars,
    pulsartargets,
    targets,
    telescopes,
)


class Mutation(
    calibrations.Mutation,
    ephemerides.Mutation,
    foldings.Mutation,
    instrumentconfigs.Mutation,
    launches.Mutation,
    observations.Mutation,
    pipelineimages.Mutation,
    pipelines.Mutation,
    processings.Mutation,
    projects.Mutation,
    pulsars.Mutation,
    pulsartargets.Mutation,
    targets.Mutation,
    telescopes.Mutation,
    graphene.ObjectType,
):
    pass
