from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Launches(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($pipeline_id: Int!, $parent_pipeline_id: Int!, $pulsar_id: Int!) {
            createLaunch(input: {
                pipeline_id: $pipeline_id,
                parent_pipeline_id: $parent_pipeline_id,
                pulsar_id: $pulsar_id
                }) {
                launch {
                    id
                }
            }
        }
        """
        # update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $pipeline_id: Int!, $parent_pipeline_id: Int!, $pulsar_id: Int!) {
            updateLaunch(id: $id, input: {
                pipeline_id: $pipeline_id,
                parent_pipeline_id: $parent_pipeline_id,
                pulsar_id: $pulsar_id
                }) {
                launch {
                    id,
                    pipeline {id},
                    parentPipeline {id},
                    pulsar {id}
                }
            }
        }
        """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteLaunch(id: $id) {
                ok
            }
        }
        """

        self.literal_field_names = ["id", "pipeline {id}", "parentPipeline {id}", "pulsar {id}"]
        self.field_names = ["id", "pipeline {name}", "parentPipeline {name}", "pulsar {jname}"]

    def list_graphql(self, id, pipeline, parentPipeline, pulsar):
        filters = [
            {"field": "pipeline", "value": pipeline, "join": "Pipelines"},
            {"field": "parentPipeline", "value": parentPipeline, "join": "Pipelines"},
            {"field": "pulsar", "value": pulsar, "join": "Pulsars"},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {
                "pipeline_id": args.pipeline_id,
                "parent_pipeline_id": args.parent_pipeline_id,
                "pulsar_id": args.pulsar_id,
            }
            return self.create_graphql()
        elif args.subcommand == "update":
            self.update_variables = {
                "id": args.id,
                "pipeline_id": args.pipeline_id,
                "parent_pipeline_id": args.parent_pipeline_id,
                "pulsar_id": args.pulsar_id,
            }
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.pipeline_id, args.parent_pipeline_id, args.pulsar_id)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "launches"

    @classmethod
    def get_description(cls):
        return "A relation between a pulsar and which pipelines are run on those pulsars"

    @classmethod
    def get_parsers(cls):
        """Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Launches model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing launches")
        parser_list.add_argument("--id", type=int, help="list launches matching the id")
        parser_list.add_argument("--pipeline_id", type=int, help="list launches matching the pipeline id")
        parser_list.add_argument(
            "--parent_pipeline_id", type=int, help="list launches matching the parent pipeline id"
        )
        parser_list.add_argument("--pulsar_id", type=int, help="list launches matching the pulsar id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new launches")
        parser_create.add_argument("pipeline_id", type=int, help="id of the pipeline")
        parser_create.add_argument("parent_pipeline_id", type=int, help="id of the parent pipeline")
        parser_create.add_argument("pulsar_id", type=int, help="id of the pulsar")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update an existing launches")
        parser_update.add_argument("id", type=int, help="id of the launch")
        parser_update.add_argument("pipeline_id", type=int, help="id of the pipeline")
        parser_update.add_argument("parent_pipeline_id", type=int, help="id of the parent pipeline")
        parser_update.add_argument("pulsar_id", type=int, help="id of the pulsar")

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing launch")
        parser_delete.add_argument("id", type=int, help="id of the launch")


if __name__ == "__main__":
    parser = Launches.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)

    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Launches(client, args.url, args.token)
    t.process(args)