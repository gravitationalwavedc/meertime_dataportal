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

        self.update_mutation = """
        mutation ($id: Int!, $target: Int!, $calibration: Int!, $telescope: Int!, $instrument_config: Int!, $project: Int!, $config: JSONString!, $duration: Float!, $utc_start: DateTime!, $nant: Int!,   $nant_eff: Int!, $suspect: Boolean!, $comment: String) {
            updateObservation(id: $id, input: {
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
                    id,
                    target { id },
                    calibration { id },
                    telescope { id },
                    instrumentConfig { id },
                    project { id },
                    config,
                    utcStart,
                    duration,
                    nant,
                    nantEff,
                    suspect,
                    comment
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

    def list_graphql(self, args):
        filters = [
            {"field": "target_Id", "join": "Targets"},
            {"field": "target_Name", "join": "Targets"},
            {"field": "telescope_Id", "join": "Telescopes"},
            {"field": "telescope_Name", "join": "Telescopes"},
            {"field": "project_Id", "join": "Projects"},
            {"field": "project_Code", "join": "Projects"},
            {"field": "instrumentConfig_Id", "join": "InstrumentConfigs"},
            {"field": "instrumentConfig_Name", "join": "InstrumentConfigs"},
            {"field": "utcStart_Gte", "join": None},
            {"field": "utcStart_Lte", "join": None},
        ]
        fields = []
        for f in filters:
            if hasattr(args, f["field"]) and not getattr(args, f["field"]) is None:
                f["value"] = getattr(args, f["field"])
                fields.append(f)

        if args.id is not None:
            self.list_query = self.build_list_id_query("observation", args.id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        elif len(fields) > 0:
            self.list_query = self.build_filter_query(fields)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def create(
        self,
        target,
        calibration,
        telescope,
        instrument_config,
        project,
        config,
        utc,
        duration,
        nant,
        nanteff,
        suspect,
        comment,
    ):
        self.create_variables = {
            "target": target,
            "calibration": calibration,
            "telescope": telescope,
            "instrument_config": instrument_config,
            "project": project,
            "config": config,
            "utc_start": utc,
            "duration": duration,
            "nant": nant,
            "nant_eff": nanteff,
            "suspect": suspect,
            "comment": comment,
        }
        return self.create_graphql()

    def update(
        self,
        id,
        target,
        calibration,
        telescope,
        instrument_config,
        project,
        config,
        utc,
        duration,
        nant,
        nanteff,
        suspect,
        comment,
    ):
        self.update_variables = {
            "id": id,
            "target": target,
            "calibration": calibration,
            "telescope": telescope,
            "instrument_config": instrument_config,
            "project": project,
            "config": config,
            "utc_start": utc,
            "duration": duration,
            "nant": nant,
            "nant_eff": nanteff,
            "suspect": suspect,
            "comment": comment,
        }
        return self.update_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(
                args.target,
                args.calibration,
                args.telescope,
                args.instrument_config,
                args.project,
                args.config,
                args.utc,
                args.duration,
                args.nant,
                args.nanteff,
                args.suspect,
                args.comment,
            )
        elif args.subcommand == "update":
            return self.update(
                args.id,
                args.target,
                args.calibration,
                args.telescope,
                args.instrument_config,
                args.project,
                args.config,
                args.utc,
                args.duration,
                args.nant,
                args.nanteff,
                args.suspect,
                args.comment,
            )
        elif args.subcommand == "list":
            return self.list_graphql(args)

    @classmethod
    def get_name(cls):
        return "observations"

    @classmethod
    def get_description(cls):
        return "Observation details."

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Observations model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing observations")
        parser_list.add_argument("--id", type=int, help="list observations matching the id")
        parser_list.add_argument("--target_Id", type=int, help="list observations matching the target id")
        parser_list.add_argument("--target_Name", type=str, help="list observations matching the target Name")
        parser_list.add_argument("--telescope_Id", type=int, help="list observations matching the telescope id")
        parser_list.add_argument("--telescope_Name", type=str, help="list observations matching the telescope name")
        parser_list.add_argument(
            "--instrumentConfig_Id", type=int, help="list observations matching the instrument_config id"
        )
        parser_list.add_argument(
            "--instrumentConfig_Name", type=str, help="list observations matching the instrument_config name"
        )
        parser_list.add_argument("--project_Id", type=int, help="list observations matching the project id")
        parser_list.add_argument("--project_Code", type=str, help="list observations matching the project code")
        parser_list.add_argument(
            "--utcStart_Gte", type=str, help="list observations with utc_start greater than the timestamp"
        )
        parser_list.add_argument(
            "--utcStart_Lte", type=str, help="list observations with utc_start greater than the timestamp"
        )

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

        parser_update = subs.add_parser("update", help="create a new observation")
        parser_update.add_argument("id", type=int, help="database id of the existing observation")
        parser_update.add_argument("target", type=int, help="target id of the observation")
        parser_update.add_argument("calibration", type=int, help="calibration id of the observation")
        parser_update.add_argument("telescope", type=int, help="telescope id of the observation")
        parser_update.add_argument("instrument_config", type=int, help="instrument config id of the observation")
        parser_update.add_argument("project", type=int, help="project id of the observation")
        parser_update.add_argument("config", type=str, help="json config of the observation")
        parser_update.add_argument("utc", type=str, help="start utc of the observation")
        parser_update.add_argument("duration", type=float, help="duration of the observation in seconds")
        parser_update.add_argument("nant", type=int, help="number of antennas used during the observation")
        parser_update.add_argument(
            "nanteff", type=int, help="effective number of antennas used during the observation"
        )
        parser_update.add_argument("suspect", type=bool, help="status of the observation")
        parser_update.add_argument("comment", type=str, help="any comment on the observation")


if __name__ == "__main__":
    parser = Observations.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Observations(client, args.url, args.token)
    t.process(args)
