import logging
from tables.graphql_table import GraphQLTable


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
                    nbin,
                    npol,
                    nchan,
                    dm,
                    tsubint
                }
            }
        }
        """
        self.field_names = ["id", "nbin", "npol", "nchan", "dm", "tsubint"]

    def list_graphql(self, id):
        if id is not None:
            self.list_query = self.build_list_id_query("folding", id)
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
                "processing_id": args.processing,
                "folding_ephemeris_id": args.eph,
                "nbin": args.nbin,
                "npol": args.npol,
                "nchan": args.nchan,
                "dm": args.dm,
                "tsubint": args.tsubint,
            }
            return self.create_graphql()
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
            return self.list_graphql(args.id)

    @classmethod
    def get_name(cls):
        return "foldings"

    @classmethod
    def get_description(cls):
        return "Folding of data to produce an archive."

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing pipelines")
        parser_list.add_argument("--id", type=int, help="list pipelines matching the id")
        parser_list.add_argument("--name", type=str, help="list pipelines matching the name")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new folding")
        parser_create.add_argument("processing", type=int, help="processing id of the folding")
        parser_create.add_argument("eph", type=str, help="ephemeris id of the folding")
        parser_create.add_argument("nbin", type=int, help="Number o bins in the folding")
        parser_create.add_argument("npol", type=int, help="Number o polarisations in the folding")
        parser_create.add_argument("nchan", type=int, help="Number o channels in the folding")
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Foldings.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Foldings(client, args.url, args.token[0])
    t.process(args)
