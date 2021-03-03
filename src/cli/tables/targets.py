import logging
from tables.graphql_table import GraphQLTable


class Targets(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($name: String!, $raj: String!, $decj: String!) {
            createTarget(name: $name, raj: $raj, decj: $decj) {
                target {
                    id
                }
            }
        }
        """
        self.create_variables = """
        {
            "name": "%s",
            "raj": "%s",
            "decj": "%s"
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $name: String!, $raj: String!, $decj: String!) {
            updateTarget(id: $id, name: $name, raj: $raj, decj: $decj) {
                target {
                    id,
                    name,
                    raj,
                    decj
                }
            }
        }
        """
        self.update_variables = """
        {
            "id": %d,
            "name": "%s",
            "raj": "%s",
            "decj": "%s"
        }
        """

    def list_graphql(self, id, name):
        if id is None and name is not None:
            self.list_query = """
            query targetsByName($name: String!) {
                targetsByName(name: $name) {
                    id,
                    name,
                    raj,
                    decj
                    }
            }
            """
            self.list_variables = """
            {
                "name": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (name))
        elif id is not None and name is None:
            self.list_query = """
            query targetById($id: Int!) {
                targetById(id: $id) {
                    id,
                    name,
                    raj,
                    decj
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
            query AllTargets {
                targets {
                    id,
                    name,
                    raj,
                    decj
                    }
            }
            """
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create_graphql((args.name, args.raj, args.decj))
        elif args.subcommand == "update":
            return self.update_graphql((args.id, args.name, args.raj, args.decj))
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.name)

    @classmethod
    def get_name(cls):
        return "targets"

    @classmethod
    def get_description(cls):
        return "J2000 position on the sky in RA and DEC with a target name"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser('list', help='list existing targets')
        parser_list.add_argument('--id', type=int, help='list targets matching the id')
        parser_list.add_argument('--name', type=str, help='list targets matching the name')

        # create the parser for the "create" command
        parser_create = subs.add_parser('create', help='create a new target')
        parser_create.add_argument('name', type=str, help='name of the target')
        parser_create.add_argument('raj', type=str, help='right ascension string in J2000 coordinates')
        parser_create.add_argument('decj', type=str, help='declincation string in J2000 coordnates')

        # create the parser for the "update" command
        parse_update = subs.add_parser('update', help='update the values of an existing target')
        parse_update.add_argument('id', type=int, help='database id of the target')
        parse_update.add_argument('name', type=str, help='name of the target')
        parse_update.add_argument('raj', type=str, help='right ascension string in J2000 coordinates')
        parse_update.add_argument('decj', type=str, help='declincation string in J2000 coordnates')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Targets.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Targets(client, args.url, args.token[0])
    t.process(args)
