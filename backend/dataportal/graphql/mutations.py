import graphene
from dataportal.graphql.mutation_tables import (
    pulsar,
    observation,
    calibration,
    ephemeris,
    telescope,
    main_project,
    project,
    template,
    pipeline_run,
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
        graphene.ObjectType,
    ):
    pass