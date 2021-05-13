from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Pipelines(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)
        self.record_name = "pipeline"

        # create a new record
        self.create_mutation = """
        mutation ($name: String!, $description: String!, $revision: String!, $createdAt: DateTime!, $createdBy: String!, $configuration: JSONString!) {
            createPipeline(input: { 
                name: $name,
                description: $description,
                revision: $revision,
                created_at: $createdAt,
                created_by: $createdBy,
                configuration: $configuration
            }) {
                pipeline {
                    id
                }
            }
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $name: String!, $description: String!, $revision: String!, $createdAt: DateTime!, $createdBy: String!, $configuration: JSONString!) {
            updatePipeline(id: $id, input: { 
                name: $name,
                description: $description,
                revision: $revision,
                created_at: $createdAt,
                created_by: $createdBy,
                configuration: $configuration
            }) {
                pipeline {
                    id,
                    name,
                    description,
                    revision,
                    createdAt,
                    createdBy,
                    configuration
                }
            }
        }
        """
        self.field_names = ["id", "name", "description", "revision", "createdAt", "createdBy", "configuration"]

    def list_graphql(self, id, name):
        filters = [
            {"field": "name", "value": name, "join": None},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def create(self, name, description, revision, created_at, created_by, configuration):
        self.create_variables = {
            "name": name,
            "description": description,
            "revision": revision,
            "createdAt": created_at,
            "createdBy": created_by,
            "configuration": configuration,
        }
        return self.create_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(
                args.name, args.description, args.revision, args.created_at, args.created_by, args.configuration,
            )
        elif args.subcommand == "update":
            self.update_variables = {
                "id": args.id,
                "name": args.name,
                "description": args.description,
                "revision": args.revision,
                "createdAt": args.created_at,
                "createdBy": args.created_by,
                "configuration": args.configuration,
            }
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.name)

    @classmethod
    def get_name(cls):
        return "pipelines"

    @classmethod
    def get_description(cls):
        return "Processing pipeline on the telescope instrument or data centre."

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Pipelines model parser")
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
        parser_list.add_argument("--name", type=str, help="list pipelines matching the name")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new pipeline")
        parser_create.add_argument("name", type=str, help="name of the pipeline")
        parser_create.add_argument("description", type=str, help="description of the pipeline")
        parser_create.add_argument("revision", type=str, help="distinguishing version for the pipeline")
        parser_create.add_argument("created_at", type=str, help="date of the pipeline creation")
        parser_create.add_argument("created_by", type=str, help="author of the pipeline")
        parser_create.add_argument("configuration", type=str, help="json config of the pipeline")

        # create the parser for the "update" command
        parse_update = subs.add_parser("update", help="update the values of an existing pipeline")
        parse_update.add_argument("id", type=int, help="database id of the pipeline")
        parse_update.add_argument("name", type=str, help="name of the pipeline")
        parse_update.add_argument("description", type=str, help="description of the pipeline")
        parse_update.add_argument("revision", type=str, help="distinguishing version for the pipeline")
        parse_update.add_argument("created_at", type=str, help="date of the pipeline creation")
        parse_update.add_argument("created_by", type=str, help="author of the pipeline")
        parse_update.add_argument("configuration", type=str, help="json config of the pipeline")


if __name__ == "__main__":
    parser = Pipelines.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Pipelines(client, args.url, args.token)
    t.process(args)
