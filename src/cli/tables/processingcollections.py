from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


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
                    id,
                    processing {id},
                    collection {id}
                }
            }
        }
        """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteProcessingcollection(id: $id) {
                ok
            }
        }
        """

        self.literal_field_names = ["id", "processing {id}", "collection {id}"]
        self.field_names = ["id", "processing {id}", "collection {name}"]

    def list_graphql(self, id, processing):
        filters = [
            {"field": "processing", "value": processing, "join": None},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

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
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "processingcollections"

    @classmethod
    def get_description(cls):
        return "A relation between a processing and a collection"

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("ProcessingCollections model parser")
        cls.configure_parsers(parser)
        return parser

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

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing processingcollection")
        parser_delete.add_argument("id", type=int, help="id of the processingcollection")


if __name__ == "__main__":
    parser = Processingcollections.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Processingcollections(client, args.url, args.token)
    t.process(args)
