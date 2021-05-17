from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Ephemerides(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($pulsar: Int!, $created_at: DateTime!, $created_by: String!, $ephemeris: JSONString!, $p0: Decimal!, $dm: Float!, $rm: Float!, $comment: String!, $valid_from: DateTime!, $valid_to: DateTime!) {
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

        self.update_mutation = """
        mutation ($id: Int!, $pulsar: Int!, $created_at: DateTime!, $created_by: String!, $ephemeris: JSONString!, $p0: Decimal!, $dm: Float!, $rm: Float!, $comment: String!, $valid_from: DateTime!, $valid_to: DateTime!) {
            updateEphemeris (id: $id, input: {
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
                    id,
                    pulsar {id},
                    createdAt,
                    createdBy,
                    ephemeris,
                    p0,
                    dm,
                    rm,
                    comment,
                    validFrom,
                    validTo
                }
            }
        }
        """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteEphemeris(id: $id) {
                ok
            }
        }
        """

        self.field_names = ["id", "pulsar {jname}", "createdAt", "createdBy", "p0", "dm", "rm", "ephemeris"]
        self.literal_field_names = ["id", "pulsar {id}", "createdAt", "createdBy", "p0", "dm", "rm", "ephemeris"]

    def list_graphql(self, id, pulsar_id, p0, dm, rm):

        # P0 is stored with a maximum of 8 decimal places only
        m = 10 ** 8
        p0_filtered = round(p0 * m) / m
        filters = [
            {"field": "pulsar", "value": pulsar_id, "join": "Pulsars"},
            {"field": "p0", "value": p0_filtered, "join": None},
            {"field": "dm", "value": dm, "join": None},
            {"field": "rm", "value": rm, "join": None},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def update(self, id, pulsar, created_at, created_by, ephemeris, p0, dm, rm, comment, valid_from, valid_to):
        self.update_variables = {
            "id": id,
            "pulsar": pulsar,
            "created_at": created_at,
            "created_by": created_by,
            "ephemeris": ephemeris,
            "p0": p0,
            "dm": dm,
            "rm": rm,
            "comment": comment,
            "valid_from": valid_from,
            "valid_to": valid_to,
        }
        return self.update_graphql()

    def create(self, pulsar, created_at, created_by, ephemeris, p0, dm, rm, comment, valid_from, valid_to):
        self.create_variables = {
            "pulsar": pulsar,
            "created_at": created_at,
            "created_by": created_by,
            "ephemeris": ephemeris,
            "p0": p0,
            "dm": dm,
            "rm": rm,
            "comment": comment,
            "valid_from": valid_from,
            "valid_to": valid_to,
        }
        return self.create_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(
                args.pulsar,
                args.created_at,
                args.created_by,
                args.ephemeris,
                args.p0,
                args.dm,
                args.rm,
                args.comment,
                args.valid_from,
                args.valid_to,
            )
        elif args.subcommand == "update":
            return self.update(
                args.id,
                args.pulsar,
                args.created_at,
                args.created_by,
                args.ephemeris,
                args.p0,
                args.dm,
                args.rm,
                args.comment,
                args.valid_from,
                args.valid_to,
            )
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.pulsar, args.p0, args.dm, args.rm)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "ephemerides"

    @classmethod
    def get_description(cls):
        return "A pulsar ephemeris"

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Ephemerides model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing ephemerides")
        parser_list.add_argument("--id", type=int, help="list ephemeris matching the id")
        parser_list.add_argument("--pulsar", type=int, help="list ephemeris matching the pulsar id")
        parser_list.add_argument("--p0", type=float, help="list ephemeris matching the pulsar P0")
        parser_list.add_argument("--dm", type=float, help="list ephemeris matching the pulsar DM")
        parser_list.add_argument("--rm", type=float, help="list ephemeris matching the pulsar RM")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new ephemeris")
        parser_create.add_argument("pulsar", type=int, help="id of the pulsar for which this ephemeris applies")
        parser_create.add_argument(
            "created_at", type=str, help="creation date of the ephemeris (YYYY-MM-DDTHH:MM:SS+000:00)"
        )
        parser_create.add_argument("created_by", type=str, help="creator of the ephemeris ")
        parser_create.add_argument("ephemeris", type=str, help="JSON containing the ephemeris")
        parser_create.add_argument("p0", type=float, help="period in the ephemeris")
        parser_create.add_argument("dm", type=float, help="DM in the ephemeris")
        parser_create.add_argument("rm", type=float, help="RM in the ephemeris")
        parser_create.add_argument("comment", type=str, help="comment about the ephemeris")
        parser_create.add_argument(
            "valid_from", type=str, help="start of the validity of the ephemeris (YYYY-MM-DDTHH:MM:SS+00:00)"
        )
        parser_create.add_argument(
            "valid_to", type=str, help="end of the validity of the ephemeris (YYYY-MM-DDTHH:MM:SS+00:00)"
        )

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update an existing ephemeris")
        parser_update.add_argument("id", type=int, help="database id of the ephemeris to update")
        parser_update.add_argument("pulsar", type=int, help="id of the pulsar for which this ephemeris applies")
        parser_update.add_argument(
            "created_at", type=str, help="creation date of the ephemeris (YYYY-MM-DDTHH:MM:SS+00:00)"
        )
        parser_update.add_argument("created_by", type=str, help="creator of the ephemeris ")
        parser_update.add_argument("ephemeris", type=str, help="JSON containing the ephemeris")
        parser_update.add_argument("p0", type=float, help="period in the ephemeris")
        parser_update.add_argument("dm", type=float, help="DM in the ephemeris")
        parser_update.add_argument("rm", type=float, help="RM in the ephemeris")
        parser_update.add_argument("comment", type=str, help="comment about the ephemeris")
        parser_update.add_argument(
            "valid_from", type=str, help="start of the validity of the ephemeris (YYYY-MM-DDTHH:MM:SS+00:00)"
        )
        parser_update.add_argument(
            "valid_to", type=str, help="end of the validity of the ephemeris (YYYY-MM-DDTHH:MM:SS+00:00)"
        )

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing ephemeris")
        parser_delete.add_argument("id", type=int, help="id of the ephemeris")


if __name__ == "__main__":
    parser = Ephemerides.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Ephemerides(client, args.url, args.token)
    t.process(args)
