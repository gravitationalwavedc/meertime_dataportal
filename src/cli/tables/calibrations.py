import logging
from tables.graphql_table import GraphQLTable


class Calibrations(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($calibration_type: String!, $location: String!) {
            createCalibration(input: {
                calibration_type: $calibration_type,
                location: $location
                }) {
                calibration {
                    id
                }
            }
        }
        """

        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $calibration_type: String!, $location: String!) {
           updateCalibration(id: $id, input: {
                calibration_type: $calibration_type,
                location: $location
           }) {
               calibration {
                   id
                   calibrationType,
                   location
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

    def create(self, type, location):
        self.create_variables = {"calibration_type": type, "location": location}
        return self.create_graphql()

    def update(self, id, type, location):
        self.update_variables = {"id": id, "calibration_type": type, "location": location}
        return self.update_graphql()

    def list(self, id, type):
        return self.list_graphql(id, type)

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(args.type, args.location)
        elif args.subcommand == "list":
            return self.list(args.id, args.type)
        elif args.subcommand == "update":
            return self.update(args.id, args.type, args.location)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

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
        parser_list.add_argument("--type", type=str, help="list calibrations matching the type [pre, post or none]")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new calibration")
        parser_create.add_argument("type", type=str, help="type of the calibration [pre, post or none]")
        parser_create.add_argument("location", type=str, help="location of the calibration on the filesystem")

        parser_udpate = subs.add_parser("update", help="update the values of an existing calibration")
        parser_udpate.add_argument("id", type=int, help="database id of the calibration")
        parser_udpate.add_argument("type", type=str, help="type of the calibration [pre, post or none]")
        parser_udpate.add_argument("location", type=str, help="location of the calibration on the filesystem")


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
