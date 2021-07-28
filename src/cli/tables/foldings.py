from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Foldings(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($processing_id: Int!, $folding_ephemeris_id: Int!, $nbin: Int!, $npol: Int!, $nchan: Int!, $dm: Float!, $tsubint: Float!) {
            createFolding(input: { 
                processing_id: $processing_id,
                folding_ephemeris_id: $folding_ephemeris_id,
                nbin: $nbin,
                npol: $npol,
                nchan: $nchan,
                dm: $dm,
                tsubint: $tsubint
            }) {
                folding {
                    id
                }
            }
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $processing_id: Int!, $folding_ephemeris_id: Int!, $nbin: Int!, $npol: Int!, $nchan: Int!, $dm: Float!, $tsubint: Float!) {
            updateFolding(id: $id, input: { 
                processing_id: $processing_id,
                folding_ephemeris_id: $folding_ephemeris_id,
                nbin: $nbin,
                npol: $npol,
                nchan: $nchan,
                dm: $dm,
                tsubint: $tsubint
            }) {
                folding {
                    id,
                    processing { id },
                    foldingEphemeris { id },
                    nbin,
                    npol,
                    nchan,
                    dm,
                    tsubint
                }
            }
        }
        """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteFolding(id: $id) {
                ok
            }
        }
        """

        self.field_names = [
            "id",
            "processing { id }",
            "foldingEphemeris { id }",
            "nbin",
            "npol",
            "nchan",
            "dm",
            "tsubint",
        ]

    def list_graphql(self, id, processing_id, folding_ephemeris_id):
        filters = [
            {"field": "processingId", "value": processing_id, "join": "Processings"},
            {"field": "foldingEphemerisId", "value": folding_ephemeris_id, "join": "Ephemerides"},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def create(self, processing, eph, nbin, npol, nchan, dm, tsubint):
        self.create_variables = {
            "processing_id": processing,
            "folding_ephemeris_id": eph,
            "nbin": nbin,
            "npol": npol,
            "nchan": nchan,
            "dm": dm,
            "tsubint": tsubint,
        }
        return self.create_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(args.processing, args.eph, args.nbin, args.npol, args.nchan, args.dm, args.tsubint)
        elif args.subcommand == "update":
            self.update_variables = {
                "id": args.id,
                "processing_id": args.processing,
                "folding_ephemeris_id": args.eph,
                "nbin": args.nbin,
                "npol": args.npol,
                "nchan": args.nchan,
                "dm": args.dm,
                "tsubint": args.tsubint,
            }
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.processing, args.eph)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "foldings"

    @classmethod
    def get_description(cls):
        return "Folding of data to produce an archive."

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Foldings model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing foldings")
        parser_list.add_argument("--id", type=int, help="list foldings matching the id")
        parser_list.add_argument("--processing", type=int, help="list foldings matching the processing id")
        parser_list.add_argument("--eph", type=int, help="list foldings matching the ephemeris id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new folding")
        parser_create.add_argument("processing", type=int, help="processing id of the folding")
        parser_create.add_argument("eph", type=str, help="ephemeris id of the folding")
        parser_create.add_argument("nbin", type=int, help="Number of bins in the folding")
        parser_create.add_argument("npol", type=int, help="Number of polarisations in the folding")
        parser_create.add_argument("nchan", type=int, help="Number of channels in the folding")
        parser_create.add_argument("dm", type=float, help="DM of the folding")
        parser_create.add_argument("tsubint", type=float, help="subintegration time of the folding")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update the values of an existing folding")
        parser_update.add_argument("id", type=int, help="database id of the folding")
        parser_update.add_argument("processing", type=int, help="processing id of the folding")
        parser_update.add_argument("eph", type=str, help="ephemeris id of the folding")
        parser_update.add_argument("nbin", type=int, help="Number o bins in the folding")
        parser_update.add_argument("npol", type=int, help="Number o polarisations in the folding")
        parser_update.add_argument("nchan", type=int, help="Number o channels in the folding")
        parser_update.add_argument("dm", type=float, help="DM of the folding")
        parser_update.add_argument("tsubint", type=float, help="subintegration time of the folding")

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing folding")
        parser_delete.add_argument("id", type=int, help="id of the folding")


if __name__ == "__main__":
    parser = Foldings.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Foldings(client, args.url, args.token)
    t.process(args)
