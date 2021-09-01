"""
    CLI interface for the Basebandings model
"""

from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


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

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteBasebanding(id: $id) {
                ok
            }
        }
        """

        self.field_names = ["id", "processing { id }"]

    def list_graphql(self, id, processing_id):
        filters = [
            {"field": "processing", "value": processing_id, "join": "Processings"},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def process(self, parser_args):
        """Parse the arguments collected by the CLI."""
        if parser_args.subcommand == "create":
            self.create_variables = {
                "processing_id": parser_args.processing,
            }
            return self.create_graphql()
        elif parser_args.subcommand == "update":
            self.update_variables = {
                "id": parser_args.id,
                "processing_id": parser_args.processing,
            }
            return self.update_graphql()
        elif parser_args.subcommand == "list":
            return self.list_graphql(parser_args.id, parser_args.processing)
        elif parser_args.subcommand == "delete":
            return self.delete(parser_args.id)
        else:
            raise RuntimeError(parser_args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "basebandings"

    @classmethod
    def get_description(cls):
        return "Basebanding of data to produce an archive."

    @classmethod
    def get_parsers(cls):
        """Returns the default parser for this model"""
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
        parser_list.add_argument("--id", type=int, help="list pipelines matching the id [int]")
        parser_list.add_argument(
            "--processing", type=int, metavar='PROCID', help="list pipelines matching the processing id [int]"
        )

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new basebanding")
        parser_create.add_argument(
            "processing", type=int, metavar="PROCID", help="processing id of the basebanding [int]"
        )

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update the values of an existing basebanding")
        parser_update.add_argument("id", type=int, metavar="ID", help="id of the basebanding [int]")
        parser_update.add_argument(
            "processing", type=int, metavar="PROCID", help="processing id of the basebanding [int]"
        )

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing basebanding")
        parser_delete.add_argument("id", type=int, metavar="ID", help="id of the basebanding [int]")


if __name__ == "__main__":
    parser = Basebandings.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Basebandings(client, args.url, args.token)
    t.process(args)
