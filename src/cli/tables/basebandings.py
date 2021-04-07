"""
    CLI interface for the Basebandings model
"""

from tables.graphql_table import GraphQLTable


class Basebandings(GraphQLTable):
    """
        Extends the GraphQLTable to provide the create, update and list command line interfaces
        the Baseband model.
    """

    def __init__(self, graphql_client, url, token):

        self.create_variables = None
        self.update_variables = None
        self.list_variables = None
        self.list_query = None

        GraphQLTable.__init__(self, graphql_client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($processing_id: Int!) {
            createBasebanding(input: { 
                processing_id: $processing_id,
            }) {
                basebanding {
                    id
                }
            }
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $processing_id: Int!) {
            updateBasebanding(id: $id, input: { 
                processing_id: $processing_id,
            }) {
                basebanding {
                    id
                }
            }
        }
        """
        self.field_names = ["id", "processing { id }"]

    def list_graphql(self, basebanding_id, processing_id):
        list_args = ()
        self.list_variables = "{}"

        if basebanding_id is not None and processing_id is None:
            self.list_query = self.build_list_id_query("basebanding", basebanding_id)
        elif basebanding_id is None and processing_id is not None:
            self.list_query = self.build_list_join_id_query("Processings", "processing", processing_id)
        else:
            self.list_query = self.build_list_all_query()

        return GraphQLTable.list_graphql(self, list_args)

    def process(self, parser_args):
        """Parse the arguments collected by the CLI."""
        if parser_args.subcommand == "create":
            self.create_variables = {
                "processing_id": parser_args.processing,
            }
            return self.create_graphql()
        if parser_args.subcommand == "update":
            self.update_variables = {
                "id": parser_args.id,
                "processing_id": parser_args.processing,
            }
            return self.update_graphql()
        if parser_args.subcommand == "list":
            return self.list_graphql(parser_args.id, parser_args.processing)
        return None

    @classmethod
    def get_name(cls):
        return "basebandings"

    @classmethod
    def get_description(cls):
        return "Basebanding of data to produce an archive."

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Basebandings model parser")
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
        parser_create = subs.add_parser("create", help="create a new basebanding")
        parser_create.add_argument("processing", type=int, help="processing id of the basebanding")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update the values of an existing basebanding")
        parser_update.add_argument("id", type=int, help="database id of the basebanding")
        parser_update.add_argument("processing", type=int, help="processing id of the basebanding")


if __name__ == "__main__":
    parser = Basebandings.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Basebandings(client, args.url, args.token)
    t.process(args)
