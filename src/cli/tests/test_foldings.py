import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.foldings import Foldings as CliFoldings


def test_cli_folding_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliFoldings(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allFoldings":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_folding_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_foldings")

    processing = baker.make("dataportal.Processings")
    eph = baker.make("dataportal.Ephemerides")

    args.subcommand = "create"
    args.processing = processing.id
    args.eph = eph.id
    args.nbin = 1024
    args.npol = 2
    args.nchan = 1024
    args.dm = 12.12
    args.tsubint = 0.00064

    t = CliFoldings(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createFolding":{"folding":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_folding_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_foldings")

    # first create a record
    folding = baker.make("dataportal.Foldings")

    # then update the record we just created
    args.subcommand = "update"
    args.id = folding.id
    args.processing = "updated"
    args.eph = "updated"
    args.nbin = "updated"
    args.npol = "updated"
    args.nchan = "updated"
    args.dm = "updated"
    args.tsubint = "updated"

    t = CliFoldings(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updateFolding":{"folding":{"id":"'
        + str(folding.id).encode("utf-8")
        + b'","processing":"updated","eph":"updated","nbin":"updated","npol":"updated","nchan":"updated","dm":"updated","tsubint":"updated"}}}}'
    )
    assert response.content == expected_content
