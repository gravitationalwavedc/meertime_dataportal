from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Filterbankings(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($processing_id: Int!, $nbit: Int!, $npol: Int!, $nchan: Int!, $dm: Float!, $tsamp: Float!) {
            createFilterbanking(input: { 
                processing_id: $processing_id,
                nbit: $nbit,
                npol: $npol,
                nchan: $nchan,
                dm: $dm,
                tsamp: $tsamp
            }) {
                filterbanking {
                    id
                }
            }
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $processing_id: Int!, $nbit: Int!, $npol: Int!, $nchan: Int!, $dm: Float!, $tsamp: Float!) {
            updateFilterbanking(id: $id, input: { 
                processing_id: $processing_id,
                nbit: $nbit,
                npol: $npol,
                nchan: $nchan,
                dm: $dm,
                tsamp: $tsamp
            }) {
                filterbanking {
                    id,
                    processing { id },
                    nbit,
                    npol,
                    nchan,
                    dm,
                    tsamp
                }
            }
        }
        """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteFilterbanking(id: $id) {
                ok
            }
        }
        """

        self.field_names = ["id", "processing { id }", "nbit", "npol", "nchan", "dm", "tsamp"]

    def list_graphql(self, id, processing):
        filters = [
            {"field": "processing", "value": processing, "join": "Processings"},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def create(self, processing, nbit, npol, nchan, dm, tsamp):
        self.create_variables = {
            "processing_id": processing,
            "nbit": nbit,
            "npol": npol,
            "nchan": nchan,
            "dm": dm,
            "tsamp": tsamp,
        }
        return self.create_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {
                "processing_id": args.processing,
                "nbit": args.nbit,
                "npol": args.npol,
                "nchan": args.nchan,
                "dm": args.dm,
                "tsamp": args.tsamp,
            }
            return self.create_graphql()
        elif args.subcommand == "update":
            self.update_variables = {
                "id": args.id,
                "processing_id": args.processing,
                "nbit": args.nbit,
                "npol": args.npol,
                "nchan": args.nchan,
                "dm": args.dm,
                "tsamp": args.tsamp,
            }
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.processing)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "filterbankings"

    @classmethod
    def get_description(cls):
        return "Filterbanking of data to produce an archive."

    @classmethod
    def get_parsers(cls):
        """Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Filterbankings model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing pipelines")
        parser_list.add_argument("--id", type=int, help="list pipelines matching the id")
        parser_list.add_argument("--processing", type=str, help="list pipelines matching the processing id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new filterbanking")
        parser_create.add_argument("processing", type=int, help="processing id of the filterbanking")
        parser_create.add_argument("nbit", type=int, help="Number of bits in the filterbanking")
        parser_create.add_argument("npol", type=int, help="Number of polarisations in the filterbanking")
        parser_create.add_argument("nchan", type=int, help="Number of channels in the filterbanking")
        parser_create.add_argument("dm", type=float, help="DM of the filterbanking")
        parser_create.add_argument("tsamp", type=float, help="sampling interval of the filterbanking")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update the values of an existing filterbanking")
        parser_update.add_argument("id", type=int, help="database id of the filterbanking")
        parser_update.add_argument("processing", type=int, help="processing id of the filterbanking")
        parser_update.add_argument("nbit", type=int, help="Number o bins in the filterbanking")
        parser_update.add_argument("npol", type=int, help="Number o polarisations in the filterbanking")
        parser_update.add_argument("nchan", type=int, help="Number o channels in the filterbanking")
        parser_update.add_argument("dm", type=float, help="DM of the filterbanking")
        parser_update.add_argument("tsamp", type=float, help="sampling interval of the filterbanking")

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing filterbanking")
        parser_delete.add_argument("id", type=int, help="id of the filterbanking")


if __name__ == "__main__":
    parser = Filterbankings.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Filterbankings(client, args.url, args.token)
    t.process(args)
