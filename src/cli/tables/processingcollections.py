import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


class Processingcollections(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($processing: Int!, $collection: Int!) {
            createProcessingcollection(input: {
                processing_id: $processing,
                collection_id: $collection
                }) {
                processingcollection {
                    id
                }
            }
        }
        """
        # update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $processing: Int!, $collection: Int!) {
            updateProcessingcollection(id: $id, input: {
                processing_id: $processing,
                collection_id: $collection
                }) {
                processingcollection {
                    id
                }
            }
        }
        """
        self.literal_field_names = ["id", "processing {id}", "collection {id}"]
        self.field_names = ["id", "processing {id}", "collection {name}"]

    def list_graphql(self, id, processing):
        if id is None and processing is not None:
            self.list_query = self.build_list_str_query("processing")
            self.list_variables = """
            {
                "variable": "%s"
            }
            """
            return GraphQLTable.list_graphql(self, (processing))
        elif id is not None and processing is None:
            self.list_query = self.build_list_id_query("processingcollection", id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {"processing": args.processing, "collection": args.collection}
            return self.create_graphql()
        elif args.subcommand == "update":
            self.update_variables = {"id": args.id, "processing": args.processing, "collection": args.collection}
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.processing)

    @classmethod
    def get_name(cls):
        return "processingcollections"

    @classmethod
    def get_description(cls):
        return "A relation between a processing and a collection"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing processingcollections")
        parser_list.add_argument("--id", type=int, help="list processingcollections matching the id")
        parser_list.add_argument(
            "--processing", type=int, help="list processingcollections matching the processing id"
        )

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new processingcollection")
        parser_create.add_argument("processing", type=int, help="id of the processing")
        parser_create.add_argument("collection", type=int, help="id of the collection")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update an existing processingcollection")
        parser_update.add_argument("id", type=int, help="id of the processingcollection")
        parser_update.add_argument("processing", type=int, help="id of the processing")
        parser_update.add_argument("collection", type=int, help="id of the collection")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Processingcollections.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Processingcollections(client, args.url, args.token[0])
    t.process(args)
