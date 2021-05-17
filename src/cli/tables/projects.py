from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Projects(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($code: String!, $short: String!, $embargoPeriod: Int!, $description: String!) {
            createProject(input: {
                code: $code,
                short: $short,
                embargoPeriod: $embargoPeriod,
                description: $description
                }) {
                project {
                    id
                }
            }
        }
        """
        self.update_mutation = """
        mutation ($id: Int!, $code: String!, $short: String!, $embargoPeriod: Int!, $description: String!) {
            updateProject(id: $id, input: {
                code: $code,
                short: $short,
                embargoPeriod: $embargoPeriod,
                description: $description
                }) {
                project {
                    id,
                    code,
                    short,
                    embargoPeriod,
                    description
                }
            }
        }
        """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteProject(id: $id) {
                ok
            }
        }
        """

        self.field_names = ["id", "code", "short", "embargoPeriod", "description"]

    def list_graphql(self, id, code):
        filters = [
            {"field": "code", "value": code, "join": None},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def create(self, code, short, embargo_period, description):
        self.create_variables = {
            "code": code,
            "short": short,
            "embargoPeriod": embargo_period,
            "description": description,
        }
        return self.create_graphql()

    def update(self, id, code, short, embargo_period, description):
        self.update_variables = {
            "id": id,
            "code": code,
            "short": short,
            "embargoPeriod": embargo_period,
            "description": description,
        }
        return self.update_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(args.code, args.short, args.embargo_period, args.description)
        elif args.subcommand == "update":
            return self.update(args.id, args.code, args.short, args.embargo_period, args.description)
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.code)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "projects"

    @classmethod
    def get_description(cls):
        return "A project defined by a code, short name, embargo period and a description"

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Projects model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing projects")
        parser_list.add_argument("--id", type=int, help="list projects matching the id")
        parser_list.add_argument("--code", type=str, help="list projects matching the code")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new project")
        parser_create.add_argument("code", type=str, help="code of the project")
        parser_create.add_argument("short", type=str, help="short name of the project")
        parser_create.add_argument("embargo_period", type=int, help="emabrgo period of the project in days")
        parser_create.add_argument("description", type=str, help="description of the project")

        parser_update = subs.add_parser("update", help="update an existing project")
        parser_update.add_argument("id", type=int, help="database id of existing project")
        parser_update.add_argument("code", type=str, help="code of the project")
        parser_update.add_argument("short", type=str, help="short name of the project")
        parser_update.add_argument("embargo_period", type=int, help="emabrgo period of the project in days")
        parser_update.add_argument("description", type=str, help="description of the project")

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing project")
        parser_delete.add_argument("id", type=int, help="id of the project")


if __name__ == "__main__":
    parser = Projects.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Projects(client, args.url, args.token)
    t.process(args)
