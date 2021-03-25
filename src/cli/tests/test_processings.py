import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.processings import Processings as CliProcessings


def test_cli_processing_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None

    t = CliProcessings(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allProcessings":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_processing_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_processings")

    observation = baker.make("dataportal.Observations")
    pipeline = baker.make("dataportal.Pipelines")

    args.subcommand = "create"
    args.embargo_end = "2000-01-01T00:00:00+0000"
    args.observation = observation.id
    args.pipeline = pipeline.id
    args.parent = pipeline.id
    args.location = "updated"
    args.job_state = "updated"
    args.job_output = '{"foo": "bar"}'
    args.results = '{"foo": "bar"}'

    t = CliProcessings(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createProcessing":{"processing":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_processing_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_processings")

    # first create a record
    processing = baker.make("dataportal.Processings")

    # then update the record we just created
    args.subcommand = "update"
    args.id = processing.id
    args.observation = "updated"
    args.pipeline = "updated"
    args.parent = "updated"
    args.location = "updated"
    args.job_state = "updated"
    args.job_output = "updated"
    args.results = "updated"

    t = CliProcessings(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updateProcessing":{"processing":{"id":"'
        + str(processing.id).encode("utf-8")
        + b'","observation":"updated","pipeline":"updated","parent":"updated","location":"updated","job_state":"updated","job_output":"updated","results":"updated"}}}}'
    )
    assert response.content == expected_content
