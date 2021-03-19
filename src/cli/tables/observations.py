import logging
from tables.graphql_table import GraphQLTable


class Observations(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($target: Int!, $calibration: Int!, $telescope: Int!, $instrument_config: Int!, $project: Int!, $config: JSONString!, $duration: Float!, $utc_start: DateTime!, $nant: Int!, $nant_eff: Int!, $suspect: Boolean!, $comment: String) {
            createObservation(input: { 
                target_id: $target,
                calibration_id: $calibration,
                telescope_id: $telescope,
                instrument_config_id: $instrument_config,
                project_id: $project,
                config: $config,
                utcStart: $utc_start,
                duration: $duration,
                nant: $nant,
                nantEff: $nant_eff,
                suspect: $suspect,
                comment: $comment 
            }) {
                observation {
                    id
                }
            }
        }
        """

        self.field_names = [
            "id",
            "target { name }",
            "calibration { location }",
            "telescope { name }",
            "instrumentConfig { name }",
            "project { code }",
            "utcStart",
            "duration",
            "nant",
            "nantEff",
            "suspect",
            "comment",
        ]
        self.literal_field_names = [
            "id",
            "target { id }",
            "calibration { id }",
            "telescope { id }",
            "instrumentConfig { id }",
            "project { id }",
            "config",
            "utcStart",
            "duration",
            "nant",
            "nantEff",
            "suspect",
            "comment",
        ]

    def list_graphql(self, id):

        if id is not None and id is None:
            self.list_query = self.build_list_id_query("observation", id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {
                "target": args.target,
                "calibration": args.calibration,
                "telescope": args.telescope,
                "instrument_config": args.instrument_config,
                "project": args.project,
                "config": args.config,
                "utc_start": args.utc,
                "duration": args.duration,
                "nant": args.nant,
                "nant_eff": args.nanteff,
                "suspect": args.suspect,
                "comment": args.comment,
            }
            return self.create_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id)

    @classmethod
    def get_name(cls):
        return "observations"

    @classmethod
    def get_description(cls):
        return "Observation details."

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing observations")
        parser_list.add_argument("--id", type=int, help="list observations matching the id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new observation")
        parser_create.add_argument("target", type=int, help="target id of the observation")
        parser_create.add_argument("calibration", type=int, help="calibration id of the observation")
        parser_create.add_argument("telescope", type=int, help="telescope id of the observation")
        parser_create.add_argument("instrument_config", type=int, help="instrument config id of the observation")
        parser_create.add_argument("project", type=int, help="project id of the observation")
        parser_create.add_argument("config", type=str, help="json config of the observation")
        parser_create.add_argument("utc", type=str, help="start utc of the observation")
        parser_create.add_argument("duration", type=float, help="duration of the observation in seconds")
        parser_create.add_argument("nant", type=int, help="number of antennas used during the observation")
        parser_create.add_argument(
            "nanteff", type=int, help="effective number of antennas used during the observation"
        )
        parser_create.add_argument("suspect", type=bool, help="status of the observation")
        parser_create.add_argument("comment", type=str, help="any comment on the observation")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Observations.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Observations(client, args.url, args.token[0])
    t.process(args)
