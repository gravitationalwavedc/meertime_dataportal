from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Pulsars(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($jname: String!, $state: String!, $comment: String!) {
            createPulsar(input: {
                jname: $jname, state: $state, comment: $comment
            }) {
                pulsar {
                    id
                }
            }
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $jname: String!, $state: String!, $comment: String!) {
           updatePulsar(id: $id, input: {
                jname: $jname,
                state: $state,
                comment: $comment
            }) {
                pulsar {
                    id,
                    jname,
                    state,
                    comment
                }
            }
        }
        """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deletePulsar(id: $id) {
                ok
            }
        }
        """

        self.field_names = ["id", "jname", "state", "comment"]

    def list_graphql(self, id, jname):
        filters = [
            {"field": "jname", "value": jname, "join": None},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def create(self, jname, state, comment):
        self.create_variables = {"jname": jname, "state": state, "comment": comment}
        return self.create_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(args.jname, args.state, args.comment)
        elif args.subcommand == "update":
            self.update_variables = {"id": args.id, "jname": args.jname, "state": args.state, "comment": args.comment}
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.jname)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "pulsars"

    @classmethod
    def get_description(cls):
        return "A pulsar source defined by a J2000 name"

    @classmethod
    def get_parsers(cls):
        """Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Pulsars model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        # create the parser for the "list" command
        parser_list = subs.add_parser("list", help="list existing Pulsars")
        parser_list.add_argument("--id", type=int, help="list Pulsars matching the id")
        parser_list.add_argument("--jname", type=str, help="list Pulsars matching the jname")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new pulsar")
        parser_create.add_argument("jname", type=str, help="jname of the pulsar")
        parser_create.add_argument("state", type=str, help=",")
        parser_create.add_argument("comment", type=str, help="description of the pulsar")

        # create the parser for the "update" command
        parser_udpate = subs.add_parser("update", help="update the values of an existing pulsar")
        parser_udpate.add_argument("id", type=int, help="database id of the pulsar")
        parser_udpate.add_argument("jname", type=str, help="jname of the pulsar")
        parser_udpate.add_argument("state", type=str, help="state of the pulsar, e.g. new, solved")
        parser_udpate.add_argument("comment", type=str, help="description of the pulsar")

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing pulsar")
        parser_delete.add_argument("id", type=int, help="id of the pulsar")


if __name__ == "__main__":

    parser = Pulsars.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    p = Pulsars(client, args.url, args.token)
    response = p.process(args)