import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


class Projects(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($code: String!, $short: String!, $embargoPeriod: Int!, $description: String!) {
            createProject(code: $code, short: $short, embargoPeriod: $embargoPeriod, description: $description) {
                project {
                    id
                }
            }
        }
        """
        self.field_names = ["id", "code", "short", "embargoPeriod", "description"]

    def list_graphql(self, id, code):
        if id is None and code is not None:
            self.list_query = self.build_list_str_query("code")
            self.list_variables = """
            {
                "variable": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (code))
        elif id is not None and code is None:
            self.list_query = self.build_list_id_query("project", id)
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
                "code": args.code,
                "short": args.short,
                "embargoPeriod": args.embargo_period,
                "description": args.description,
            }
            return self.create_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.code)

    @classmethod
    def get_name(cls):
        return "projects"

    @classmethod
    def get_description(cls):
        return "A project defined by a code, short name, embargo period and a description"

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Projects.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Projects(client, args.url, args.token[0])
    t.process(args)
