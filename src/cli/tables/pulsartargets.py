from tables.graphql_table import GraphQLTable


class Pulsartargets(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($pulsar: Int!, $target: Int!) {
            createPulsartarget(input: {
                pulsar_id: $pulsar,
                target_id: $target
                }) {
                pulsartarget {
                    id
                }
            }
        }
        """
        # update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $pulsar: Int!, $target: Int!) {
            updatePulsartarget(id: $id, input: {
                pulsar_id: $pulsar,
                target_id: $target
                }) {
                pulsartarget {
                    id,
                    pulsar {id},
                    target {id}
                }
            }
        }
        """
        self.literal_field_names = ["id", "pulsar {id}", "target {id}"]
        self.field_names = ["id", "pulsar {jname}", "target {name}"]

    def list_graphql(self, args):
        filters = [
            {"arg": "target_id", "field": "target_Id", "join": "Targets"},
            {"arg": "target_name", "field": "target_Name", "join": "Targets"},
            {"arg": "pulsar_id", "field": "pulsar_Id", "join": "Pulsars"},
            {"arg": "pulsar_jname", "field": "pulsar_Jname", "join": "Pulsars"},
        ]
        fields = []
        for f in filters:
            if hasattr(args, f["arg"]) and not getattr(args, f["arg"]) is None:
                f["value"] = getattr(args, f["arg"])
                fields.append(f)

        if args.id is not None:
            self.list_query = self.build_list_id_query("pulsartarget", args.id)
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

    def create(self, pulsar, target):
        self.create_variables = {"pulsar": pulsar, "target": target}
        return self.create_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(args.pulsar, args.target)
        elif args.subcommand == "update":
            self.update_variables = {"id": args.id, "pulsar": args.pulsar, "target": args.target}
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args)

    @classmethod
    def get_name(cls):
        return "pulsartargets"

    @classmethod
    def get_description(cls):
        return "A relation between a pulsar and a target"

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("PulsarTargets model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing pulsartargets")
        parser_list.add_argument("--id", type=int, help="list pulsartargets matching the id")
        parser_list.add_argument("--pulsar_id", type=int, help="list pulsartargets matching the pulsar id")
        parser_list.add_argument("--pulsar_jname", type=str, help="list pulsartargets matching the pulsar Jname")
        parser_list.add_argument("--target_id", type=int, help="list pulsartargets matching the target id")
        parser_list.add_argument("--target_name", type=str, help="list pulsartargets matching the target name")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new pulsartarget")
        parser_create.add_argument("pulsar", type=int, help="id of the pulsar")
        parser_create.add_argument("target", type=int, help="id of the target")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update an existing pulsartarget")
        parser_update.add_argument("id", type=int, help="id of the pulsartarget")
        parser_update.add_argument("pulsar", type=int, help="id of the pulsar")
        parser_update.add_argument("target", type=int, help="id of the target")


if __name__ == "__main__":
    parsers = Pulsartargets.get_parsers()
    args = parsers.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Pulsartargets(client, args.url, args.token)
    t.process(args)
