import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


class Calibrations(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($type: String!, $location: String!) {
            createCalibration(type: $type, location: $location) {
                calibration {
                    id
                }
            }
        }
        """
        self.field_names = ["id", "calibrationType", "location"]

    def list_graphql(self, id, type):
        if id is None and type is not None:
            self.list_query = self.build_list_str_query("calibration_type")
            self.list_variables = """
            {
                "variable": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (type))
        elif id is not None and type is None:
            self.list_query = self.build_list_id_query("calibration", id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {"type": args.type, "location": args.location}
            return self.create_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.type)

    @classmethod
    def get_name(cls):
        return "calibrations"

    @classmethod
    def get_description(cls):
        return "A defined by its type and location"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing calibrations")
        parser_list.add_argument("--id", type=int, help="list calibrations matching the id")
        parser_list.add_argument("--type", type=str, help="list calibrations matching the type")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new calibration")
        parser_create.add_argument("type", type=str, help="type of the calibration")
        parser_create.add_argument("location", type=str, help="location of the calibration")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Calibrations.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Calibrations(client, args.url, args.token[0])
    t.process(args)
