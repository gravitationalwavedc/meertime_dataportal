import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.pipelineimages import Pipelineimages as CliPipelineimages


def test_cli_pipelineimage_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None

    t = CliPipelineimages(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allPipelineimages":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_pipelineimage_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_pipelineimages")

    processing = baker.make(
        "dataportal.Processings", observation__target__name="test", observation__instrument_config__beam="test",
    )

    args.subcommand = "create"
    args.processing_id = processing.id
    args.image = __file__
    args.image_type = "test"
    args.rank = 99

    t = CliPipelineimages(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createPipelineimage":{"pipelineimage":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_pipelineimage_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_pipelineimages")

    # first create a record
    pipelineimage = baker.make("dataportal.Pipelineimages")

    # then update the record we just created
    args.subcommand = "update"
    args.id = pipelineimage.id
    args.processing_id = "updated"
    args.image = "updated"

    t = CliPipelineimages(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updatePipelineimage":{"pipelineimage":{"id":"'
        + str(pipelineimage.id).encode("utf-8")
        + b'","processing_id":"updated","image":"updated"}}}}'
    )
    assert response.content == expected_content
