import logging
from cli.tables.graphql_table import GraphQLTable


class Pipelines(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($name: String!, $description: String!, $revision: String!, $createdAt: DateTime!, $createdBy: String!, $configuration: String!) {
            createPipeline(input: { 
                name: $name,
                description: $description,
                revision: $revision,
                createdAt: $createdAt,
                createdBy: $createdBy,
                configuration: $configuration
            }) {
                pipeline {
                    id
                }
            }
        }
        """
        self.create_variables = """
        {
            "name": "%s",
            "description": "%s",
            "revision": "%s",
            "createdAt": "%s",
            "createdBy": "%s",
            "configuration": "%s"
        }
        """
        # Update an existing record
        self.update_mutation = """
        mutation ($id: Int!, $name: String!, $description: String!, $revision: String!, $createdAt: DateTime!, $createdBy: String!, $configuration: String!) {
            updatePipeline(id: $id, input: { 
                name: $name,
                description: $description,
                revision: $revision,
                createdAt: $createdAt,
                createdBy: $createdBy,
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
        self.update_variables = """
        {
            "id": %d,
            "name": "%s",
            "description": "%s",
            "revision": "%s",
            "createdAt": "%s",
            "createdBy": "%s",
            "configuration": "%s"
         }
        """

    def list_graphql(self, id, name):
        if id is None and name is not None:
            self.list_query = """
            query pipelinesByName($name: String!) {
                pipelinesByName(name: $name) {
                    id,
                    name,
                    description,
                    revision,
                    createdAt,
                    createdBy,
                    configuration
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
            query pipelineById($id: Int!) {
                pipelineById(id: $id) {
                    id,
                    name,
                    description,
                    revision,
                    createdAt,
                    createdBy,
                    configuration
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
            query AllPipelines {
                pipelines {
                    id,
                    name,
                    description,
                    revision,
                    createdAt,
                    createdBy,
                    configuration
                }
            }
            """
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            return self.create_graphql(
                (args.name, args.description, args.revision, args.created_at, args.created_by, args.configuration)
            )
        elif args.subcommand == "update":
            return self.update_graphql(
                (
                    args.id,
                    args.name,
                    args.description,
                    args.revision,
                    args.created_at,
                    args.created_by,
                    args.configuration,
                )
            )
        elif args.subcommand == "list":
            return self.list_graphql(args.id, args.name)

    @classmethod
    def get_name(cls):
        return "pipelines"

    @classmethod
    def get_description(cls):
        return "Processing pipeline on the telescope instrument or data centre."

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        # create the parser for the "list" command
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand", required=True)

        parser_list = subs.add_parser('list', help='list existing pipelines')
        parser_list.add_argument('--id', type=int, help='list pipelines matching the id')
        parser_list.add_argument('--name', type=str, help='list pipelines matching the name')

        # create the parser for the "create" command
        parser_create = subs.add_parser('create', help='create a new pipeline')
        parser_create.add_argument('name', type=str, help='name of the pipeline')
        parser_create.add_argument('description', type=str, help='description of the pipeline')
        parser_create.add_argument('revision', type=str, help='distinguishing version for the pipeline')
        parser_create.add_argument('created_at', type=str, help='date of the pipeline creation')
        parser_create.add_argument('created_by', type=str, help='author of the pipeline')
        parser_create.add_argument('configuration', type=str, help='author of the pipeline')

        # create the parser for the "update" command
        parse_update = subs.add_parser('update', help='update the values of an existing pipeline')
        parse_update.add_argument('id', type=int, help='database id of the pipeline')
        parse_update.add_argument('name', type=str, help='name of the pipeline')
        parse_update.add_argument('description', type=str, help='description of the pipeline')
        parse_update.add_argument('revision', type=str, help='distinguishing version for the pipeline')
        parse_update.add_argument('created_at', type=str, help='date of the pipeline creation')
        parse_update.add_argument('created_by', type=str, help='author of the pipeline')
        parse_update.add_argument('configuration', type=str, help='author of the pipeline')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Pipelines.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    t = Pipelines(client, args.url, args.token[0])
    t.process(args)