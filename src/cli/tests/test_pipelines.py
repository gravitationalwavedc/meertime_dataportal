import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.pipelines import Pipelines as CliPipelines


def test_cli_pipeline_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliPipelines(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allPipelines":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_pipeline_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_pipelines")

    args.subcommand = "create"
    args.name = "updated"
    args.description = "updated"
    args.revision = "updated"
    args.created_at = "2000-01-01T00:00:00+0000"
    args.created_by = "updated"
    args.configuration = '{"foo":"bar"}'

    t = CliPipelines(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createPipeline":{"pipeline":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_pipeline_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_pipelines")

    # first create a record
    pipeline = baker.make("dataportal.Pipelines")

    # then update the record we just created
    args.subcommand = "update"
    args.id = pipeline.id
    args.name = "updated"
    args.description = "updated"
    args.revision = "updated"
    args.created_at = "updated"
    args.created_by = "updated"
    args.configuration = "updated"

    t = CliPipelines(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updatePipeline":{"pipeline":{"id":"'
        + str(pipeline.id).encode("utf-8")
        + b'","name":"updated","description":"updated","revision":"updated","created_at":"updated","created_by":"updated","configuration":"updated"}}}}'
    )
    assert response.content == expected_content
