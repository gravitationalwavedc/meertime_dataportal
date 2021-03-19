import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


class Pulsartargets(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($pulsar: Int!, $target: Int!) {
            createPulsartarget(input: {
                pulsar_id: $pulsar,
                target_id: $target
                }) {
                pulsartarget {
                    id
                }
            }
        }
        """
        # update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $pulsar: Int!, $target: Int!) {
            updatePulsartarget(id: $id, input: {
                pulsar_id: $pulsar,
                target_id: $target
                }) {
                pulsartarget {
                    id
                }
            }
        }
        """
        self.literal_field_names = ["id", "pulsar {id}", "target {id}"]
        self.field_names = ["id", "pulsar {jname}", "target {name}"]

    def list_graphql(self, id, pulsar):
        if id is None and pulsar is not None:
            self.list_query = self.build_list_str_query("pulsar")
            self.list_variables = """
            {
                "variable": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (pulsar))
        elif id is not None and pulsar is None:
            self.list_query = self.build_list_id_query("pulsartarget", id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {"pulsar": args.pulsar, "target": args.target}
            return self.create_graphql()
        elif args.subcommand == "update":
            self.update_variables = {"id": args.id, "pulsar": args.pulsar, "target": args.target}
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.pulsar)

    @classmethod
    def get_name(cls):
        return "pulsartargets"

    @classmethod
    def get_description(cls):
        return "A relation between a pulsar and a target"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing pulsartargets")
        parser_list.add_argument("--id", type=int, help="list pulsartargets matching the id")
        parser_list.add_argument("--pulsar", type=int, help="list pulsartargets matching the pulsar id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new pulsartarget")
        parser_create.add_argument("pulsar", type=int, help="id of the pulsar")
        parser_create.add_argument("target", type=int, help="id of the target")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update an existing pulsartarget")
        parser_update.add_argument("id", type=int, help="id of the pulsartarget")
        parser_update.add_argument("pulsar", type=int, help="id of the pulsar")
        parser_update.add_argument("target", type=int, help="id of the target")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Pulsartargets.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Pulsartargets(client, args.url, args.token[0])
    t.process(args)
