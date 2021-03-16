import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


class Instrumentconfigs(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($name: String!, $bandwidth: Decimal!, $frequency: Decimal!, $nchan: Int!, $npol: Int!, $beam: String!) {
            createInstrumentconfig(name: $name, bandwidth: $bandwidth, frequency: $frequency, nchan: $nchan, npol: $npol, beam: $beam) {
                instrumentconfig {
                    id
                }
            }
        }
        """
        self.field_names = ["id", "name", "frequency", "bandwidth", "nchan", "npol", "beam"]

    def list_graphql(self, id, name, beam):
        if id is None and name is not None:
            self.list_query = self.build_list_str_query("name")
            self.list_variables = """
            {
                "variable": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (name))
        elif id is None and beam is not None:
            self.list_query = self.build_list_str_query("beam")
            self.list_variables = """
            {
                "variable": "%s"
            }
            """
        elif id is not None and name is None and beam is None:
            self.list_query = self.build_list_id_query("instrumentconfig", id)
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
                "name": args.name,
                "bandwidth": args.bandwidth,
                "frequency": args.frequency,
                "nchan": args.nchan,
                "npol": args.npol,
                "beam": args.beam,
            }
            return self.create_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.name, args.beam)

    @classmethod
    def get_name(cls):
        return "instrumentconfigs"

    @classmethod
    def get_description(cls):
        return "An instrument configuration defined by a name, bandwidth, frequency, nchan, npol, and beam"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing instrument configurations")
        parser_list.add_argument("--id", type=int, help="list instrument configuration matching the id")
        parser_list.add_argument("--name", type=str, help="list instrument configuration matching the name")
        parser_list.add_argument("--beam", type=str, help="list instrument configuration matching the beam")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new instrument configuration")
        parser_create.add_argument("name", type=str, help="name of the instrument configuration")
        parser_create.add_argument("frequency", type=float, help="frequency of the instrument configuration")
        parser_create.add_argument("bandwidth", type=float, help="bandwidth of the instrument configuration")
        parser_create.add_argument("nchan", type=int, help="number of channels of the instrument configuration")
        parser_create.add_argument("npol", type=int, help="number of polarisation of the instrument configuration")
        parser_create.add_argument("beam", type=str, help="beam description of the instrument configuration")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Instrumentconfigs.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Instrumentconfigs(client, args.url, args.token[0])
    t.process(args)
