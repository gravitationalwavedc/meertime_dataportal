import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.launches import Launches as CliLaunches


def test_cli_launch_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None
    args.pipeline_id = None
    args.pulsar_id = None

    t = CliLaunches(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allLaunches":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_launch_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_launches")

    pipeline = baker.make("dataportal.Pipelines")
    pulsar = baker.make("dataportal.Pulsars")

    args.subcommand = "create"
    args.pipeline_id = pipeline.id
    args.parent_pipeline_id = pipeline.id
    args.pulsar_id = pulsar.id

    t = CliLaunches(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createLaunche":{"launche":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_launch_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_launches")

    # first create a record
    launche = baker.make("dataportal.Launches")

    # then update the record we just created
    args.subcommand = "update"
    args.id = launche.id
    args.pipeline_id = "updated"
    args.parent_pipeline_id = "updated"
    args.pulsar_id = "updated"

    t = CliLaunches(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updateLaunche":{"launche":{"id":"'
        + str(launche.id).encode("utf-8")
        + b'","pipeline_id":"updated","parent_pipeline_id":"updated","pulsar_id":"updated"}}}}'
    )
    assert response.content == expected_content
