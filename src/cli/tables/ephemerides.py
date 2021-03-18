import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


class Ephemerides(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($pulsar: Int!, $created_at: DateTime!, $created_by: String!, $ephemeris: JSONString!, $p0: Float!, $dm: Float!, $rm: Float!, $comment: String!, $valid_from: DateTime!, $valid_to: DateTime!) {
            createEphemeris (input: {
                pulsar_id: $pulsar,
                created_at: $created_at,
                created_by: $created_by,
                ephemeris: $ephemeris,
                p0: $p0,
                dm: $dm,
                rm: $rm,
                comment: $comment,
                valid_from: $valid_from,
                valid_to: $valid_to
                }) {
                ephemeris {
                    id
                }    
            }
        }
        """

        self.field_names = ["id", "createdAt", "createdBy", "p0"]

    def list_graphql(self, id):
        if id is not None:
            self.list_query = self.build_list_id_query("ephemeris", id)
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
                "pulsar": args.pulsar,
                "created_at": args.created_at,
                "created_by": args.created_by,
                "ephemeris": args.ephemeris,
                "p0": args.p0,
                "dm": args.dm,
                "rm": args.rm,
                "comment": args.comment,
                "valid_from": args.valid_from,
                "valid_to": args.valid_to,
            }
            return self.create_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id)

    @classmethod
    def get_name(cls):
        return "ephemerides"

    @classmethod
    def get_description(cls):
        return "A pulsar ephemeris"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing ephemerides")
        parser_list.add_argument("--id", type=int, help="list ephemeris matching the id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new ephemeris")
        parser_create.add_argument("pulsar", type=int, help="id of the pulsar for which this ephemeris applies")
        parser_create.add_argument(
            "created_at", type=str, help="creation date of the ephemeris (YYYY-MM-DDTHH:MM:SS+00000)"
        )
        parser_create.add_argument("created_by", type=str, help="creator of the ephemeris ")
        parser_create.add_argument("ephemeris", type=str, help="JSON containing the ephemeris")
        parser_create.add_argument("p0", type=float, help="period in the ephemeris")
        parser_create.add_argument("dm", type=float, help="DM in the ephemeris")
        parser_create.add_argument("rm", type=float, help="RM in the ephemeris")
        parser_create.add_argument("comment", type=str, help="comment about the ephemeris")
        parser_create.add_argument(
            "valid_from", type=str, help="start of the validity of the ephemeris (YYYY-MM-DDTHH:MM:SS+0000)"
        )
        parser_create.add_argument(
            "valid_to", type=str, help="end of the validity of the ephemeris (YYYY-MM-DDTHH:MM:SS+0000)"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Ephemerides.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Ephemerides(client, args.url, args.token[0])
    t.process(args)
