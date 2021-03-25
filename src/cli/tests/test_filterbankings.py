import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.filterbankings import Filterbankings as CliFilterbankings


def test_cli_filterbanking_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None
    args.processing = None

    t = CliFilterbankings(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allFilterbankings":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_filterbanking_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_filterbankings")

    processing = baker.make("dataportal.Processings")

    args.subcommand = "create"
    args.processing = processing.id
    args.nbit = 8
    args.npol = 2
    args.nchan = 1024
    args.dm = 12.12
    args.tsamp = 0.00064

    t = CliFilterbankings(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createFilterbanking":{"filterbanking":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_filterbanking_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_filterbankings")

    # first create a record
    filterbanking = baker.make("dataportal.Filterbankings")

    # then update the record we just created
    args.subcommand = "update"
    args.id = filterbanking.id
    args.processing = "updated"
    args.nbit = "updated"
    args.npol = "updated"
    args.nchan = "updated"
    args.dm = "updated"
    args.tsamp = "updated"

    t = CliFilterbankings(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updateFilterbanking":{"filterbanking":{"id":"'
        + str(filterbanking.id).encode("utf-8")
        + b'","processing":"updated","nbit":"updated","npol":"updated","nchan":"updated","dm":"updated","tsamp":"updated"}}}}'
    )
    assert response.content == expected_content
