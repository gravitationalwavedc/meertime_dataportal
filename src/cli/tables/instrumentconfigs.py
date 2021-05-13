from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Instrumentconfigs(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($name: String!, $bandwidth: Decimal!, $frequency: Decimal!, $nchan: Int!, $npol: Int!, $beam: String!) {
            createInstrumentconfig(input: {
                name: $name,
                bandwidth: $bandwidth,
                frequency: $frequency,
                nchan: $nchan,
                npol: $npol,
                beam: $beam
                }) {
                instrumentconfig {
                    id
                }
            }
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $name: String!, $bandwidth: Decimal!, $frequency: Decimal!, $nchan: Int!, $npol: Int!, $beam: String!) {
            updateInstrumentconfig(id: $id, input: {
                name: $name,
                bandwidth: $bandwidth,
                frequency: $frequency,
                nchan: $nchan,
                npol: $npol,
                beam: $beam
                }) {
                instrumentconfig {
                    id,
                    name,
                    bandwidth,
                    frequency,
                    nchan,
                    npol,
                    beam
                }
            }
        }
        """
        self.field_names = ["id", "name", "frequency", "bandwidth", "nchan", "npol", "beam"]

    def list_graphql(self, id, name, beam):
        filters = [
            {"field": "name", "value": name, "join": None},
            {"field": "beam", "value": beam, "join": None},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def create(self, name, bandwidth, frequency, nchan, npol, beam):
        self.create_variables = {
            "name": name,
            "bandwidth": bandwidth,
            "frequency": frequency,
            "nchan": nchan,
            "npol": npol,
            "beam": beam,
        }
        return self.create_graphql()

    def update(self, id, name, bandwidth, frequency, nchan, npol, beam):
        self.update_variables = {
            "id": id,
            "name": name,
            "bandwidth": bandwidth,
            "frequency": frequency,
            "nchan": nchan,
            "npol": npol,
            "beam": beam,
        }
        return self.update_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(args.name, args.bandwidth, args.frequency, args.nchan, args.npol, args.beam)
        elif args.subcommand == "update":
            return self.update(args.id, args.name, args.bandwidth, args.frequency, args.nchan, args.npol, args.beam)
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.name, args.beam)

    @classmethod
    def get_name(cls):
        return "instrumentconfigs"

    @classmethod
    def get_description(cls):
        return "An instrument configuration defined by a name, bandwidth, frequency, nchan, npol, and beam"

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("InstrumentConfigs model parser")
        cls.configure_parsers(parser)
        return parser

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

        # create the parser for the "create" command
        parser_create = subs.add_parser("update", help="update an existing instrument configuration")
        parser_create.add_argument("id", type=int, help="database id of the instrument configuration")
        parser_create.add_argument("name", type=str, help="name of the instrument configuration")
        parser_create.add_argument("frequency", type=float, help="frequency of the instrument configuration")
        parser_create.add_argument("bandwidth", type=float, help="bandwidth of the instrument configuration")
        parser_create.add_argument("nchan", type=int, help="number of channels of the instrument configuration")
        parser_create.add_argument("npol", type=int, help="number of polarisation of the instrument configuration")
        parser_create.add_argument("beam", type=str, help="beam description of the instrument configuration")


if __name__ == "__main__":

    parser = Instrumentconfigs.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Instrumentconfigs(client, args.url, args.token)
    t.process(args)
