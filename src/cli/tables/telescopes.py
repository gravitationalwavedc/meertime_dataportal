import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


class Telescopes(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($name: String!) {
            createTelescope(input: {
                name: $name,
                }) {
                telescope {
                    id
                }
            }
        }
        """

        self.field_names = ["id", "name"]

    def list_graphql(self, id, name):
        if id is None and name is not None:
            self.list_query = self.build_list_str_query("name")
            self.list_variables = """
            {
                "variable": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (name))
        elif id is not None and name is None:
            self.list_query = self.build_list_id_query("telescope", id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {"name": args.name}
            return self.create_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.name)

    @classmethod
    def get_name(cls):
        return "telescopes"

    @classmethod
    def get_description(cls):
        return "A telescope defined by a name"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing telescopes")
        parser_list.add_argument("--id", type=int, help="list telescopes matching the id")
        parser_list.add_argument("--name", type=str, help="list telescopes matching the name")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new telescope")
        parser_create.add_argument("name", type=str, help="name of the telescope")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Telescopes.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Telescopes(client, args.url, args.token[0])
    t.process(args)
