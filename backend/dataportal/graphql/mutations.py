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
        graphene.ObjectType,
    ):
    pass