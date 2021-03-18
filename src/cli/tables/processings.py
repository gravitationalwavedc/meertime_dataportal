import logging
from tables.graphql_table import GraphQLTable


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
                    id
                }
            }
        }       """
        self.field_names = ["id", "location", "embargoEnd", "jobState", "jobOutput", "results"]

    def list_graphql(self, id):
        if id is not None:
            self.list_query = self.build_list_id_query("processing", id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            self.create_variables = {
                "observation_id": args.observation,
                "pipeline_id": args.pipeline,
                "parent_id": args.parent,
                "embargo_end": args.embargo_end,
                "location": args.location,
                "job_state": args.job_state,
                "job_output": args.job_output,
                "results": args.results,
            }
            return self.create_graphql()
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
            return self.list_graphql(args.id)

    @classmethod
    def get_name(cls):
        return "processings"

    @classmethod
    def get_description(cls):
        return "Processing."

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        parser_list = subs.add_parser("list", help="list existing processings")
        parser_list.add_argument("--id", type=int, help="list processing matching the id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new pipeline")
        parser_create.add_argument("observation", type=int, help="observation id for the processing")
        parser_create.add_argument("pipeline", type=int, help="pipeline id for the processing")
        parser_create.add_argument("parent", type=int, help="parent id for the processing")
        parser_create.add_argument(
            "embargo_end", type=str, help="end of embargo of the processing (YYYY-MM-DDTHH:MM:SS+0000)"
        )
        parser_create.add_argument("location", type=str, help="location (on disk) of the processing)")
        parser_create.add_argument("job_state", type=str, help="JSON with the state of the processing)")
        parser_create.add_argument("job_output", type=str, help="JSON with output of the processing)")
        parser_create.add_argument("results", type=str, help="JSON with results of the processing)")

        # create the parser for the "update" command
        parser_update = subs.add_parser("update", help="update the values of an existing processing")
        parser_update.add_argument("id", type=int, help="id of the processing")
        parser_update.add_argument("observation", type=int, help="observation id for the processing")
        parser_update.add_argument("pipeline", type=int, help="pipeline id for the processing")
        parser_update.add_argument("parent", type=int, help="parent id for the processing")
        parser_update.add_argument(
            "embargo_end", type=str, help="end of embargo of the processing (YYYY-MM-DDTHH:MM:SS+0000)"
        )
        parser_update.add_argument("location", type=str, help="location (on disk) of the processing)")
        parser_update.add_argument("job_state", type=str, help="JSON with the state of the processing)")
        parser_update.add_argument("job_output", type=str, help="JSON with output of the processing)")
        parser_update.add_argument("results", type=str, help="JSON with results of the processing)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Processings.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Processings(client, args.url, args.token[0])
    t.process(args)
