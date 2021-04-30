from joins.graphql_join import GraphQLJoin


class FoldedObservations(GraphQLJoin):
    def __init__(self, client, url, token):
        GraphQLJoin.__init__(self, client, url, token)

        self.table_name = "foldings"
        self.join_prefix = "processing_Observation_"

        self.literal_field_names = [
            "id",
            "foldingEphemeris { id }",
            "nbin",
            "npol",
            "nchan",
            "dm",
            "tsubint,",
            """
            processing {
                observation {
                    target { id } 
                    telescope { id } 
                    calibration { id } 
                    project { id } 
                    instrument_config { id } 
                    utc_start
                }
            }
            """,
        ]
        self.field_names = [
            "id",
            "foldingEphemeris { id }",
            "nbin",
            "npol",
            "nchan",
            "dm",
            "tsubint",
            """
            foldingEphemeris {
                pulsar { jname }
            }
            """,
            """
            processing {
                observation {
                    target {
                        name
                    },
                    telescope { name } 
                    calibration { id } 
                    project { code } 
                    instrumentConfig { id } 
                    utcStart
                }
            }
            """,
        ]

    def list_graphql(self, args):

        filters = [
            {"arg": "pulsar_id", "field": "foldingEphemeris_Pulsar_Id", "join": "Pulsars"},
            {"arg": "pulsar_jname", "field": "foldingEphemeris_Pulsar_Jname", "join": "Pulsars"},
            {"arg": "telescope_id", "field": "processing_Observation_Telescope_Id", "join": "Telescopes"},
            {"arg": "telescope_name", "field": "processing_Observation_Telescope_Name", "join": "Telescopes"},
            {"arg": "project_id", "field": "processing_Observation_Project_Id", "join": "Projects"},
            {"arg": "project_code", "field": "processing_Observation_Project_Code", "join": "Projects"},
            {
                "arg": "instrument_config_id",
                "field": "processing_Observation_InstrumentConfig_Id",
                "join": "InstrumentConfigs",
            },
            {
                "arg": "instrument_config_name",
                "field": "processing_Observation_InstrumentConfig_Name",
                "join": "InstrumentConfigs",
            },
            {"arg": "utc_start_gte", "field": "processing_Observation_UtcStart_Gte", "join": None},
            {"arg": "utc_start_lte", "field": "processing_Observation_UtcStart_Lte", "join": None},
        ]
        fields = []
        for f in filters:
            if hasattr(args, f["arg"]) and not getattr(args, f["arg"]) is None:
                f["value"] = getattr(args, f["arg"])
                fields.append(f)

        if len(fields) > 0:
            self.list_query = self.build_filter_query(fields)
            self.list_variables = "{}"
            return GraphQLJoin.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLJoin.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "list":
            return self.list_graphql(args)

    @classmethod
    def get_name(cls):
        return "foldedobservations"

    @classmethod
    def get_description(cls):
        return "Folded Observations"

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLJoin.get_default_parser("Folded observations")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing folded observations")
        parser_list.add_argument("--pulsar_id", type=int, help="list folded observations matching the pulsar id")
        parser_list.add_argument("--pulsar_jname", type=str, help="list folded observations matching the pulsar jname")
        parser_list.add_argument("--telescope_id", type=int, help="list folded observations matching the telescope id")
        parser_list.add_argument(
            "--telescope_name", type=str, help="list folded observations matching the telescope name"
        )
        parser_list.add_argument(
            "--instrument_config_id", type=int, help="list folded observations matching the instrument_config id"
        )
        parser_list.add_argument(
            "--instrument_config_name", type=str, help="list folded observations matching the instrument_config name"
        )
        parser_list.add_argument("--project_id", type=int, help="list folded observations matching the project id")
        parser_list.add_argument("--project_code", type=str, help="list folded observations matching the project code")
        parser_list.add_argument(
            "--utc_start_gte", type=str, help="list folded observations with utc_start greater than the timestamp"
        )
        parser_list.add_argument(
            "--utc_start_lte", type=str, help="list folded observations with utc_start less than the timestamp"
        )


if __name__ == "__main__":
    parser = FoldedObservations.get_parsers()
    args = parser.parse_args()

    GraphQLJoin.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = FoldedObservations(client, args.url, args.token)
    t.process(args)
