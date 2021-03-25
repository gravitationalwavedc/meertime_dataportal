import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.pulsartargets import Pulsartargets as CliPulsartargets


def test_cli_pulsartarget_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None
    args.pulsar = None

    t = CliPulsartargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allPulsartargets":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_pulsartarget_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_pulsartargets")

    pulsar = baker.make("dataportal.Pulsars")
    target = baker.make("dataportal.Targets")

    args.subcommand = "create"
    args.pulsar = pulsar.id
    args.target = target.id

    t = CliPulsartargets(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createPulsartarget":{"pulsartarget":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_pulsartarget_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_pulsartargets")

    # first create a record
    pulsartarget = baker.make("dataportal.Pulsartargets")

    # then update the record we just created
    args.subcommand = "update"
    args.id = pulsartarget.id
    args.pulsar = "updated"
    args.target = "updated"

    t = CliPulsartargets(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updatePulsartarget":{"pulsartarget":{"id":"'
        + str(pulsartarget.id).encode("utf-8")
        + b'","pulsar":"updated","target":"updated"}}}}'
    )
    assert response.content == expected_content
