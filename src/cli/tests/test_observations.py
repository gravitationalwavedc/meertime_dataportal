import re
from model_bakery import baker
from cli.tests.helpers import *
from cli.tables.observations import Observations as CliObservations


def test_cli_observation_list_with_token(client, creator, args, jwt_token):
    args.subcommand = "list"
    args.id = None

    t = CliObservations(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"allObservations":{"edges":\[*\]}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_observation_create_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_observations")

    target = baker.make("dataportal.Targets")
    calibration = baker.make("dataportal.Calibrations")
    telescope = baker.make("dataportal.Telescopes")
    ic = baker.make("dataportal.Instrumentconfigs")
    project = baker.make("dataportal.Projects")

    args.subcommand = "create"
    args.target = target.id
    args.calibration = calibration.id
    args.telescope = telescope.id
    args.instrument_config = ic.id
    args.project = project.id
    args.config = "{}"
    args.utc = "2000-01-01T00:00:00+0000"
    args.duration = 2134.5
    args.nant = 64
    args.nanteff = 64
    args.suspect = "updated"
    args.comment = "updated"

    t = CliObservations(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content_pattern = b'{"data":{"createObservation":{"observation":{"id":"\d+"}}}}'
    compiled_pattern = re.compile(expected_content_pattern)
    assert compiled_pattern.match(response.content)


def test_cli_observation_update_with_token(client, creator, args, jwt_token):
    assert creator.has_perm("dataportal.add_observations")

    # first create a record
    observation = baker.make("dataportal.Observations")

    # then update the record we just created
    args.subcommand = "update"
    args.id = observation.id
    args.target = "updated"
    args.calibration = "updated"
    args.telescope = "updated"
    args.instrument_config = "updated"
    args.project = "updated"
    args.config = "updated"
    args.utc = "updated"
    args.duration = "updated"
    args.nant = "updated"
    args.suspect = "updated"
    args.comment = "updated"

    t = CliObservations(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200

    expected_content = (
        b'{"data":{"updateObservation":{"observation":{"id":"'
        + str(observation.id).encode("utf-8")
        + b'","target":"updated","calibration":"updated","telescope":"updated","instrument_config":"updated","project":"updated","config":"updated","utc":"updated","duration":"updated","nant":"updated","suspect":"updated","comment":"updated"}}}}'
    )
    assert response.content == expected_content
