# Please note these tests are expected to be run from src directory, not from cli, i.e., they need to use the poetry environment from the main project, not the environment defined in this directory
import pytest
import json
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from dataportal.models import (
    Basebandings,
    Calibrations,
    Collections,
    Ephemerides,
    Filterbankings,
    Foldings,
    Instrumentconfigs,
    Launches,
    Observations,
    Pipelineimages,
    Pipelines,
    Processingcollections,
    Processings,
    Projects,
    Pulsars,
    Pulsartargets,
    Targets,
    Telescopes,
)

# need to modify the sys path to get the tests to work properly
import sys

sys.path.append("cli")

from cli.tables.basebandings import Basebandings as CliBasebandings
from cli.tables.calibrations import Calibrations as CliCalibrations
from cli.tables.collections import Collections as CliCollections
from cli.tables.ephemerides import Ephemerides as CliEphemerides
from cli.tables.filterbankings import Filterbankings as CliFilterbankings
from cli.tables.foldings import Foldings as CliFoldings
from cli.tables.instrumentconfigs import Instrumentconfigs as CliInstrumentconfigs
from cli.tables.launches import Launches as CliLaunches
from cli.tables.observations import Observations as CliObservations
from cli.tables.pipelineimages import Pipelineimages as CliPipelineimages
from cli.tables.pipelines import Pipelines as CliPipelines
from cli.tables.processingcollections import Processingcollections as CliProcessingcollections
from cli.tables.processings import Processings as CliProcessings
from cli.tables.projects import Projects as CliProjects
from cli.tables.pulsars import Pulsars as CliPulsars
from cli.tables.pulsartargets import Pulsartargets as CliPulsartargets
from cli.tables.targets import Targets as CliTargets
from cli.tables.telescopes import Telescopes as CliTelescopes

from cli.graphql_client import GraphQLClient


# Auxiliary functions
jwt_mutation = """
    mutation TokenAuth($username: String!, $password: String!) {
        tokenAuth(input:{username: $username, password: $password}) {
            token
            payload
            refreshExpiresIn
        }
    }
"""


def __create_viewer(client, django_user_model):
    username = "viewer"
    password = "reweiv"
    viewer = django_user_model.objects.create_user(username=username, password=password)
    return viewer


jwt_vars_viewer = """
    {
        "username": "viewer",
        "password":  "reweiv"
    }
"""


@pytest.fixture
def creator(django_user_model):
    username = "creator"
    password = "rotaerc"
    creator = django_user_model.objects.create_user(username=username, password=password)

    content_type = ContentType.objects.get_for_model(Basebandings)
    permission = Permission.objects.get(content_type=content_type, codename="add_basebandings")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Calibrations)
    permission = Permission.objects.get(content_type=content_type, codename="add_calibrations")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Collections)
    permission = Permission.objects.get(content_type=content_type, codename="add_collections")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Ephemerides)
    permission = Permission.objects.get(content_type=content_type, codename="add_ephemerides")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Filterbankings)
    permission = Permission.objects.get(content_type=content_type, codename="add_filterbankings")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Foldings)
    permission = Permission.objects.get(content_type=content_type, codename="add_foldings")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Instrumentconfigs)
    permission = Permission.objects.get(content_type=content_type, codename="add_instrumentconfigs")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Launches)
    permission = Permission.objects.get(content_type=content_type, codename="add_launches")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Observations)
    permission = Permission.objects.get(content_type=content_type, codename="add_observations")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Pipelineimages)
    permission = Permission.objects.get(content_type=content_type, codename="add_pipelineimages")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Pipelines)
    permission = Permission.objects.get(content_type=content_type, codename="add_pipelines")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Processingcollections)
    permission = Permission.objects.get(content_type=content_type, codename="add_processingcollections")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Processings)
    permission = Permission.objects.get(content_type=content_type, codename="add_processings")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Projects)
    permission = Permission.objects.get(content_type=content_type, codename="add_projects")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Pulsars)
    permission = Permission.objects.get(content_type=content_type, codename="add_pulsars")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Pulsartargets)
    permission = Permission.objects.get(content_type=content_type, codename="add_pulsartargets")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Targets)
    permission = Permission.objects.get(content_type=content_type, codename="add_targets")
    creator.user_permissions.add(permission)

    content_type = ContentType.objects.get_for_model(Telescopes)
    permission = Permission.objects.get(content_type=content_type, codename="add_telescopes")
    creator.user_permissions.add(permission)

    return creator


jwt_vars_creator = """
    {
        "username": "creator",
        "password":  "rotaerc"
    }
"""


def __obtain_jwt_token(client, mutation, vars):
    # obtain the token
    payload = {"query": mutation, "variables": vars}
    response = client.post("/graphql/", payload)
    data = json.loads(response.content)["data"]
    jwt_token = data["tokenAuth"]["token"]
    return jwt_token


def __obtain_default_args():
    class Struct(object):
        pass

    args = Struct()
    args.subcommand = None
    args.verbose = False
    args.very_verbose = False
    return args


# Test cli.tables.targets
def test_cli_target_parser():
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Database models which can be interrogated")

    target_parser = subparsers.add_parser(CliTargets.get_name(), help=CliTargets.get_description())
    CliTargets.configure_parsers(target_parser)


@pytest.mark.django_db
def test_cli_target_create_with_token(client, creator):
    assert creator.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "create"
    args.name = "name"
    args.raj = "raj"
    args.decj = "decj"

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createTarget":{"target":{"id":"1"}}}}'


@pytest.mark.django_db
def test_cli_target_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allTargets":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_target_list_with_name_and_token(client, creator):
    assert creator.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = "name"

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allTargets":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_target_list_with_id_and_token(client, creator):
    assert creator.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = 1
    args.name = None

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    # assert response.content == b'{"data":{"targetById":[]}}'


@pytest.mark.django_db
def test_cli_target_update_with_token(client, creator):
    assert creator.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()

    # first create a record
    args = __obtain_default_args()
    args.subcommand = "create"
    args.name = "name"
    args.raj = "raj"
    args.decj = "decj"

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createTarget":{"target":{"id":"2"}}}}'

    content = json.loads(response.content)
    # then udpate a record
    args.subcommand = "update"
    args.id = int(content["data"]["createTarget"]["target"]["id"])
    args.name = "name2"
    args.raj = "raj2"
    args.decj = "decj2"
    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200
    assert (
        response.content
        == b'{"data":{"updateTarget":{"target":{"id":"2","name":"name2","raj":"raj2","decj":"decj2"}}}}'
    )


# Tests for cli.tables.pulsars
def test_cli_pulsar_parser():
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Database models which can be interrogated")

    pulsar_parser = subparsers.add_parser(CliPulsars.get_name(), help=CliPulsars.get_description())
    CliPulsars.configure_parsers(pulsar_parser)


@pytest.mark.django_db
def test_cli_pulsar_create_with_token(client, creator):
    assert creator.has_perm("dataportal.add_pulsars")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "create"
    args.jname = "J1234-1234"
    args.state = "state"
    args.comment = "comment"

    t = CliPulsars(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createPulsar":{"pulsar":{"id":"1"}}}}'


@pytest.mark.django_db
def test_cli_pulsar_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_pulsars")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.jname = None

    t = CliPulsars(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allPulsars":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_pulsar_update_with_token(client, creator):
    assert creator.has_perm("dataportal.add_pulsars")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)

    # first create a record
    args = __obtain_default_args()
    args.subcommand = "create"
    args.jname = "jname"
    args.state = "state"
    args.comment = "comment"

    t = CliPulsars(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createPulsar":{"pulsar":{"id":"2"}}}}'

    content = json.loads(response.content)
    # then udpate a record
    args.subcommand = "update"
    args.id = int(content["data"]["createPulsar"]["pulsar"]["id"])
    args.jname = "jname2"
    args.state = "state2"
    args.comment = "comment2"
    t = CliPulsars(client, "/graphql/", jwt_token)
    response = t.process(args)

    assert response.status_code == 200
    assert (
        response.content
        == b'{"data":{"updatePulsar":{"pulsar":{"id":"2","jname":"jname2","state":"state2","comment":"comment2"}}}}'
    )


@pytest.mark.django_db
def test_cli_basebandings_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_basebandings")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.processing = None

    t = CliBasebandings(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allBasebandings":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_calibrations_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_calibrations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.type = None

    t = CliCalibrations(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allCalibrations":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_collections_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_collections")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliCollections(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allCollections":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_ephemerides_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_ephemerides")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None

    t = CliEphemerides(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allEphemerides":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_filterbankings_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_filterbankings")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.processing = None

    t = CliFilterbankings(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allFilterbankings":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_foldings_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_foldings")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliFoldings(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allFoldings":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_instrumentconfigs_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_instrumentconfigs")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = None
    args.beam = None

    t = CliInstrumentconfigs(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allInstrumentconfigs":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_launches_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_launches")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.pipeline_id = None
    args.pulsar_id = None

    t = CliLaunches(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allLaunches":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_observations_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None

    t = CliObservations(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allObservations":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_pipelineimages_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_pipelineimages")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None

    t = CliPipelineimages(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allPipelineimages":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_pipelines_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_pipelines")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliPipelines(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allPipelines":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_processingcollections_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_processingcollections")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.processing = None

    t = CliProcessingcollections(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allProcessingcollections":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_processings_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_processings")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None

    t = CliProcessings(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allProcessings":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_projects_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_projects")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.code = None

    t = CliProjects(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allProjects":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_pulsartargets_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_pulsartargets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.pulsar = None

    t = CliPulsartargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allPulsartargets":{"edges":[]}}}'


@pytest.mark.django_db
def test_cli_telescopes_list_with_token(client, creator):
    assert creator.has_perm("dataportal.add_telescopes")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliTelescopes(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"allTelescopes":{"edges":[]}}}'


# test collections creation
@pytest.mark.django_db
def test_cli_collections_create_with_token(client, creator):
    assert creator.has_perm("dataportal.add_collections")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "create"
    args.name = "foo"
    args.description = "foo"

    t = CliCollections(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createCollection":{"collection":{"id":"1"}}}}'


# test telescopes creation
@pytest.mark.django_db
def test_cli_telescopes_create_with_token(client, creator):
    assert creator.has_perm("dataportal.add_telescopes")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "create"
    args.name = "foo"

    t = CliTelescopes(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createTelescope":{"telescope":{"id":"1"}}}}'


def test_graphql_client():
    url = "http://127.0.0.1:8000/graphql"
    verbose = False
    client = GraphQLClient(url, verbose)
    try:
        client.connect()
    except:
        print("Caught connection exception")
