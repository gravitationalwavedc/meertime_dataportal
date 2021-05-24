from tables.graphql_table import GraphQLTable
from tables.graphql_query import graphql_query_factory


class Processings(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($observation_id: Int!, $pipeline_id: Int!, $parent_id: Int!, $embargo_end: DateTime!, $location: String!, $job_state: JSONString!, $job_output: JSONString!, $results: JSONString!) {
            createProcessing(input: {
                observation_id: $observation_id,
                pipeline_id: $pipeline_id,
                parent_id: $parent_id,
                embargo_end: $embargo_end,
                location: $location,
                job_state: $job_state,
                job_output: $job_output,
                results: $results
            }) {
                processing {
                    id
                }
            }
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $observation_id: Int!, $pipeline_id: Int!, $parent_id: Int!, $embargo_end: DateTime!, $location: String!, $job_state: JSONString!, $job_output: JSONString!, $results: JSONString!) {
            updateProcessing(id: $id, input: {
                observation_id: $observation_id,
                pipeline_id: $pipeline_id,
                parent_id: $parent_id,
                embargo_end: $embargo_end,
                location: $location,
                job_state: $job_state,
                job_output: $job_output,
                results: $results
            }) {
                processing {
                    id,
                    observation { id },
                    pipeline { id },
                    parent { id },
                    location,
                    embargoEnd,
                    jobState,
                    jobOutput,
                    results
                }
            }
        }       """

        self.delete_mutation = """
        mutation ($id: Int!) {
            deleteProcessing(id: $id) {
                ok
            }
        }
        """

        self.field_names = [
            "id",
            "observation { id }",
            "pipeline { name }",
            "parent { id }",
            "location",
            "embargoEnd",
            "jobState",
            "jobOutput",
            "results",
        ]
        self.literal_field_names = [
            "id",
            "observation { id }",
            "pipeline { id }",
            "parent { id } ",
            "location",
            "embargoEnd",
            "jobState",
            "jobOutput",
            "results",
        ]

    def list_graphql(self, id, observation_id, location, utc_start):
        filters = [
            {"field": "observationId", "value": observation_id, "join": "Observations"},
            {"field": "location", "value": location, "join": None},
            {"field": "observation_UtcStart_Gte", "value": utc_start, "join": "Observations"},
            {"field": "observation_UtcStart_Lte", "value": utc_start, "join": "Observations"},
        ]
        graphql_query = graphql_query_factory(self.table_name, self.record_name, id, filters)
        return GraphQLTable.list_graphql(self, graphql_query)

    def create(self, observation, pipeline, parent, embargo_end, location, job_state, job_output, results):
        self.create_variables = {
            "observation_id": observation,
            "pipeline_id": pipeline,
            "parent_id": parent,
            "embargo_end": embargo_end,
            "location": location,
            "job_state": job_state,
            "job_output": job_output,
            "results": results,
        }
        return self.create_graphql()

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create(
                args.observation,
                args.pipeline,
                args.parent,
                args.embargo_end,
                args.location,
                args.job_state,
                args.job_output,
                args.results,
            )
        elif args.subcommand == "update":
            self.update_variables = {
                "id": args.id,
                "observation_id": args.observation,
                "pipeline_id": args.pipeline,
                "parent_id": args.parent,
                "embargo_end": args.embargo_end,
                "location": args.location,
                "job_state": args.job_state,
                "job_output": args.job_output,
                "results": args.results,
            }
            return self.update_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.observation, args.location, args.utc_start)
        elif args.subcommand == "delete":
            return self.delete(args.id)
        else:
            raise RuntimeError(args.subcommand + " command is not implemented")

    @classmethod
    def get_name(cls):
        return "processings"

    @classmethod
    def get_description(cls):
        return "Processing."

    @classmethod
    def get_parsers(cls):
        """ Returns the default parser for this model"""
        parser = GraphQLTable.get_default_parser("Processings model parser")
        cls.configure_parsers(parser)
        return parser

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing processings")
        parser_list.add_argument("--id", type=int, help="list processing matching the id")
        parser_list.add_argument("--observation", type=int, help="list processing matching the observation id")
        parser_list.add_argument("--utc_start", type=str, help="list processing matching the observation utc_start")
        parser_list.add_argument("--location", type=str, help="list processing matching the processing location")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new pipeline")
        parser_create.add_argument("observation", type=int, help="observation id for the processing")
        parser_create.add_argument("pipeline", type=int, help="pipeline id for the processing")
        parser_create.add_argument("parent", type=int, help="parent id for the processing")
        parser_create.add_argument(
            "embargo_end", type=str, help="end of embargo of the processing (YYYY-MM-DDTHH:MM:SS+0000)"
        )
        parser_create.add_argument("location", type=str, help="location (on disk) of the processing")
        parser_create.add_argument("job_state", type=str, help="JSON with the state of the processing")
        parser_create.add_argument("job_output", type=str, help="JSON with output of the processing")
        parser_create.add_argument("results", type=str, help="JSON with results of the processing")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update the values of an existing processing")
        parser_update.add_argument("id", type=int, help="id of the processing")
        parser_update.add_argument("observation", type=int, help="observation id for the processing")
        parser_update.add_argument("pipeline", type=int, help="pipeline id for the processing")
        parser_update.add_argument("parent", type=int, help="parent id for the processing")
        parser_update.add_argument("location", type=str, help="location (on disk) of the processing")
        parser_update.add_argument(
            "embargo_end", type=str, help="end of embargo of the processing (YYYY-MM-DDTHH:MM:SS+0000)"
        )
        parser_update.add_argument("job_state", type=str, help="JSON with the state of the processing")
        parser_update.add_argument("job_output", type=str, help="JSON with output of the processing")
        parser_update.add_argument("results", type=str, help="JSON with results of the processing")

        # create the parser for the "delete" command
        parser_delete = subs.add_parser("delete", help="delete an existing processing")
        parser_delete.add_argument("id", type=int, help="id of the processing")


if __name__ == "__main__":
    parser = Processings.get_parsers()
    args = parser.parse_args()

    GraphQLTable.configure_logging(args)
    from graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)

    t = Processings(client, args.url, args.token)
    t.process(args)
