import logging
from cli.tables.graphql_table import GraphQLTable


class Pulsars(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
            mutation ($jname: String!, $state: String!, $comment: String!) {
                createPulsar(jname: $jname, state: $state, comment: $comment) {
                    pulsar {
                        id
                    }
                }
            }
        """
        self.create_variables = """
            {
                "jname": "%s",
                "state": "%s",
                "comment": "%s"
            }
            """
        # Update an existing record
        self.update_mutation = """
            mutation ($id: Int!, $jname: String!, $state: String!, $comment: String!) {
                updatePulsar(id: $id, jname: $jname, state: $state, comment: $comment) {
                    pulsar {
                        id,
                        jname,
                        state,
                        comment
                    }
                }
            }
        """
        self.update_variables = """
        {
            "id": %d,
            "jname": "%s",
            "state": "%s",
            "comment": "%s"
        }
        """

    def list_graphql(self, id, jname):
        if id is None and jname is not None:
            self.list_query = """
            query PulsarsByJname($jname: String!) {
                pulsarsByJname(jname: $jname) {
                    id,
                    jname,
                    state,
                    comment
                }
            }
            """
            self.list_variables = """
            {
                "jname": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (jname))
        elif id is not None and jname is None:
            self.list_query = """
            query pulsarById($id: Int!) {
                pulsarById(id: $id) {
                    id,
                    jname,
                    state,
                    comment
                }
            }
            """
            self.list_variables = """
            {
                "id": %d
            }
            """
            return GraphQLTable.list_graphql(self, (id))
        else:
            self.list_query = """
            query AllPulsars {
                pulsars {
                    id,
                    jname,
                    state,
                    comment
                }
            }
            """
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create_graphql((args.jname, args.state, args.comment))
        elif args.subcommand == "update":
            return self.update_graphql((args.id, args.jname, args.state, args.comment))
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.jname)

    @classmethod
    def get_name(cls):
        return "pulsars"

    @classmethod
    def get_description(cls):
        return "A pulsar source defined by a J2000 name"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest='subcommand', required=True)

        # create the parser for the "list" command
        parser_list = subs.add_parser('list', help='list existing Pulsars')
        parser_list.add_argument('--id', type=int, help='list Pulsars matching the id')
        parser_list.add_argument('--jname', type=str, help='list Pulsars matching the jname')

        # create the parser for the "create" command
        parser_create = subs.add_parser('create', help='create a new pulsar')
        parser_create.add_argument('jname', type=str, help='jname of the pulsar')
        parser_create.add_argument('state', type=str, help=',')
        parser_create.add_argument('comment', type=str, help='description of the pulsar')

        # create the parser for the "create" command
        parser_udpate = subs.add_parser('update', help='update the values of an existing pulsar')
        parser_udpate.add_argument('id', type=int, help='database id of the pulsar')
        parser_udpate.add_argument('jname', type=str, help='jname of the pulsar')
        parser_udpate.add_argument('state', type=str, help='state of the pulsar, e.g. new, solved')
        parser_udpate.add_argument('comment', type=str, help='description of the pulsar')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Pulsars.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    p = Pulsars(client, args.url, args.token[0])
    response = p.process(args)
