import graphene

from dataportal.graphql.mutation_tables import (
    calibration,
    ephemeris,
    main_project,
    observation,
    pipeline_run,
    project,
    pulsar,
    residual,
    telescope,
    template,
    toa,
)


class Mutation(
    pulsar.Mutation,
    observation.Mutation,
    calibration.Mutation,
    ephemeris.Mutation,
    telescope.Mutation,
    main_project.Mutation,
    project.Mutation,
    template.Mutation,
    pipeline_run.Mutation,
    toa.Mutation,
    residual.Mutation,
    graphene.ObjectType,
):
    pass
