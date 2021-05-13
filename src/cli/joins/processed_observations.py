from joins.graphql_join import GraphQLJoin
from tables.graphql_query import graphql_query_factory


class ProcessedObservations(GraphQLJoin):
    def __init__(self, client, url, token):
        GraphQLJoin.__init__(self, client, url, token)

        self.table_name = "processings"
        self.join_prefix = "observation_"

        self.literal_field_names = [
            "id",
            """
            observation {
                target { id } 
                telescope { id } 
                calibration { id } 
                project { id } 
                instrument_config { id } 
                utc_start
            }
            """
            "pipeline { id }",
            "parent { id }",
            "location",
            "embargoEnd",
            "jobState",
            "jobOutput",
            "results",
        ]
        self.field_names = [
            "id",
            """
            observation {
                target { name } 
                telescope { name } 
                calibration { id } 
                project { code } 
                instrumentConfig { id } 
                utcStart
            }
            """,
            "pipeline { name }",
            "parent { id }",
            "location",
            "embargoEnd",
            "jobState",
            "jobOutput",
            "results",
        ]

    def list_graphql(self, args):
        filters = [
            {"value": args.target_id, "field": "observation_Target_Id", "join": "Targets"},
            {"value": args.target_name, "field": "observation_Target_Name", "join": "Targets"},
            {"value": args.telescope_id, "field": "observation_Telescope_Id", "join": "Telescopes"},
            {"value": args.telescope_name, "field": "observation_Telescope_Name", "join": "Telescopes"},
            {"value": args.project_id, "field": "observation_Project_Id", "join": "Projects"},
            {"value": args.project_code, "field": "observation_Project_Code", "join": "Projects"},
            {
                "value": args.instrument_config_id,
                "field": "observation_InstrumentConfig_Id",
                "join": "InstrumentConfigs",
            },
            {
                "value": args.instrument_config_name,
                "field": "observation_InstrumentConfig_Name",
                "join": "InstrumentConfigs",
            },
            {"value": args.utc_start_gte, "field": "observation_UtcStart_Gte", "join": None},
            {"value": args.utc_start_lte, "field": "observation_UtcStart_Lte", "join": None},
        ]

        graphql_query = graphql_query_factory(self.table_name, self.record_name, None, filters)
        return GraphQLJoin.list_graphql(self, graphql_query)

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "list":
            return self.list_graphql(args)

    @classmethod
    def get_name(cls):
        return "processedobservations"

    @classmethod
    def get_description(cls):
        return "Processed Observations"

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLJoin.get_default_parser("Processed Observations parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing processings of observations")
        parser_list.add_argument("--target_id", type=int, help="list processed observations matching the target id")
        parser_list.add_argument(
            "--target_name", type=str, help="list processed observations matching the target name"
        )
        parser_list.add_argument(
            "--telescope_id", type=int, help="list processed observations matching the telescope id"
        )
        parser_list.add_argument(
            "--telescope_name", type=str, help="list processed observations matching the telescope name"
        )
        parser_list.add_argument(
            "--instrument_config_id", type=int, help="list processed observations matching the instrument_config id"
        )
        parser_list.add_argument(
            "--instrument_config_name",
            type=str,
            help="list processed observations matching the instrument_config name",
        )
        parser_list.add_argument("--project_id", type=int, help="list processed observations matching the project id")
        parser_list.add_argument(
            "--project_code", type=str, help="list processed observations matching the project code"
        )
        parser_list.add_argument(
            "--utc_start_gte", type=str, help="list processed observations with utc_start greater than the timestamp"
        )
        parser_list.add_argument(
            "--utc_start_lte", type=str, help="list processed observations with utc_start less than the timestamp"
        )


if __name__ == "__main__":
    parser = ProcessedObservations.get_parsers()
    args = parser.parse_args()

    GraphQLJoin.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = ProcessedObservations(client, args.url, args.token)
    t.process(args)
