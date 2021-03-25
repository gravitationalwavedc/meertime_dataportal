import re
import datetime
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.ephemerides import Ephemerides as CliEphemerides


def test_cli_ephemeris_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None

    t = CliEphemerides(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allEphemerides":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_ephemeris_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_ephemerides")

    pulsar = baker.make("dataportal.Pulsars")

    args.subcommand = "create"
    args.pulsar = pulsar.id
    args.created_at = "2000-01-01T00:00:00+0000"
    args.created_by = "updated"
    args.ephemeris = '{"FO": "1234.5"}'
    args.p0 = 12.12
    args.dm = 32.32
    args.rm = 0.0
    args.comment = "updated"
    args.valid_from = "2000-01-01T00:00:00+0000"
    args.valid_to = "2001-01-01T00:00:00+0000"

    t = CliEphemerides(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createEphemeris":{"ephemeris":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_ephemeris_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_ephemerides")

    # first create a record
    ephemeride = baker.make("dataportal.Ephemerides")

    # then update the record we just created
    args.subcommand = "update"
    args.id = ephemeride.id
    args.pulsar = "updated"
    args.created_by = "updated"
    args.ephemeris = "updated"
    args.p0 = "updated"
    args.dm = "updated"
    args.rm = "updated"
    args.comment = "updated"

    t = CliEphemerides(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updateEphemeride":{"ephemeride":{"id":"'
        + str(ephemeride.id).encode("utf-8")
        + b'","pulsar":"updated","created_by":"updated","ephemeris":"updated","p0":"updated","dm":"updated","rm":"updated","comment":"updated"}}}}'
    )
    assert response.content == expected_content
