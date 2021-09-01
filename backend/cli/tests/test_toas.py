import re
import datetime
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.toas import Toas as CliToas


def test_cli_toa_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None
    args.processing = None
    args.folding = None
    args.ephemeris = None
    args.template = None
    args.flags = None
    args.frequency = None
    args.mjd = None
    args.site = None
    args.uncertainty = None
    args.quality = None
    args.comment = None

    t = CliToas(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allToas":{"edges":\\[*\\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_toa_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_toas")

    processing = baker.make("dataportal.Processings")
    folding = baker.make("dataportal.Foldings")
    ephemeris = baker.make("dataportal.Ephemerides")
    template = baker.make("dataportal.Templates")

    args.subcommand = "create"
    args.processing = processing.id
    args.folding = folding.id
    args.ephemeris = ephemeris.id
    args.template = template.id
    args.flags = "{}"
    args.frequency = 11.11
    args.mjd = "12345.6789"
    args.site = 1
    args.uncertainty = 22.22
    args.quality = "nominal"
    args.comment = "comment"

    t = CliToas(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createToa":{"toa":{"id":"\\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_toa_update_with_token(client, creator, args, jwt_token, debug_log):
    assert creator.has_perm("dataportal.add_toas")

    # first create a record
    toa = baker.make("dataportal.Toas")

    processing = baker.make("dataportal.Processings")
    folding = baker.make("dataportal.Foldings")
    ephemeris = baker.make("dataportal.Ephemerides")
    template = baker.make("dataportal.Templates")

    # then update the record we just created
    args.subcommand = "update"
    args.id = toa.id
    args.processing = processing.id
    args.folding = folding.id
    args.ephemeris = ephemeris.id
    args.template = template.id
    args.flags = "{}"
    args.frequency = 33.33
    args.mjd = "23456.7890"
    args.site = 2
    args.uncertainty = 44.44
    args.quality = "bad"
    args.comment = "updated comment"

    t = CliToas(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        '{"data":{"updateToa":{"toa":{'
        + '"id":"'
        + str(toa.id)
        + '",'
        + '"processing":{"id":"'
        + t.encode_table_id("Processings", args.processing)
        + '"},'
        + '"inputFolding":{"id":"'
        + t.encode_table_id("Foldings", args.folding)
        + '"},'
        + '"timingEphemeris":{"id":"'
        + t.encode_table_id("Ephemerides", args.ephemeris)
        + '"},'
        + '"template":{"id":"'
        + t.encode_table_id("Templates", args.template)
        + '"},'
        + '"flags":"'
        + args.flags
        + '",'
        + '"frequency":'
        + str(args.frequency)
        + ','
        + '"mjd":"'
        + args.mjd
        + '",'
        + '"site":'
        + str(args.site)
        + ','
        + '"uncertainty":'
        + str(args.uncertainty)
        + ','
        + '"quality":"'
        + args.quality.upper()
        + '",'
        + '"comment":"'
        + args.comment
        + '"}}}}'
    )

    assert response.content == expected_content.encode("utf-8")


def test_cli_toa_delete_with_token(client, creator, args, jwt_token, debug_log):
    assert creator.has_perm("dataportal.add_toas")

    # first create a record
    toa = baker.make("dataportal.Toas")

    # then update the record we just created
    args.subcommand = "delete"
    args.id = toa.id

    t = CliToas(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = '{"data":{"deleteToa":{"ok":true}}}'

    assert response.content == expected_content.encode("utf-8")
