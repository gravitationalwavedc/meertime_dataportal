import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.instrumentconfigs import Instrumentconfigs as CliInstrumentconfigs


def test_cli_instrumentconfig_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None
    args.name = None
    args.beam = None

    t = CliInstrumentconfigs(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allInstrumentconfigs":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_instrumentconfig_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_instrumentconfigs")

    args.subcommand = "create"
    args.name = "updated"
    args.frequency = 1234.1234
    args.bandwidth = 800.0
    args.nchan = 1024
    args.npol = 2
    args.beam = 1

    t = CliInstrumentconfigs(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createInstrumentconfig":{"instrumentconfig":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_instrumentconfig_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_instrumentconfigs")

    # first create a record
    instrumentconfig = baker.make("dataportal.Instrumentconfigs")

    # then update the record we just created
    args.subcommand = "update"
    args.id = instrumentconfig.id
    args.name = "updated"
    args.frequency = "updated"
    args.bandwidth = "updated"
    args.nchan = "updated"
    args.npol = "updated"
    args.beam = "updated"

    t = CliInstrumentconfigs(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updateInstrumentconfig":{"instrumentconfig":{"id":"'
        + str(instrumentconfig.id).encode("utf-8")
        + b'","name":"updated","frequency":"updated","bandwidth":"updated","nchan":"updated","npol":"updated","beam":"updated"}}}}'
    )
    assert response.content == expected_content
