from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


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

        self.delete_mutation = """
        mutation ($id: Int!) {
            deletePulsartarget(id: $id) {
                ok
            }
        }
        """

        self.literal_field_names = ["id", "pulsar {id}", "target {id}"]
        self.field_names = ["id", "pulsar {jname}", "target {name}"]

    def list_graphql(self, id, target_id, target_name, pulsar_id, pulsar_jname):
        filters = [
            {"field": "target_Id", "value": target_id, "join": "Targets"},
            {"field": "target_Name", "value": target_name, "join": "Targets"},
            {"field": "pulsar_Id", "value": pulsar_id, "join": "Pulsars"},
            {"field": "pulsar_Jname", "value": pulsar_jname, "join": "Pulsars"},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

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
            return self.list_graphql(args.id, args.target, args.target_name, args.pulsar, args.pulsar_jname)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "pulsartargets"

    @classmethod
    def get_description(cls):
        return "A relation between a pulsar and a target"

    @classmethod
    def get_parsers(cls):
        """Returns the default parser for this model"""
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
        parser_list.add_argument("--pulsar", type=int, help="list pulsartargets matching the pulsar id")
        parser_list.add_argument("--pulsar_jname", type=str, help="list pulsartargets matching the pulsar Jname")
        parser_list.add_argument("--target", type=int, help="list pulsartargets matching the target id")
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

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing pulsartarget")
        parser_delete.add_argument("id", type=int, help="id of the pulsartarget")


if __name__ == "__main__":
    parsers = Pulsartargets.get_parsers()
    args = parsers.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Pulsartargets(client, args.url, args.token)
    t.process(args)