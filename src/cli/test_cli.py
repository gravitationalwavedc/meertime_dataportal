import pytest
import json
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

from dataportal.models import Pulsars, Targets

from cli.tables.pulsars import Pulsars as CliPulsars
from cli.tables.targets import Targets as CliTargets
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


def __create_creator(client, django_user_model):
    username = "creator"
    password = "rotaerc"
    creator = django_user_model.objects.create_user(username=username, password=password)
    content_type = ContentType.objects.get_for_model(Targets)
    permission = Permission.objects.get(content_type=content_type, codename="add_targets")
    content_type = ContentType.objects.get_for_model(Pulsars)
    permission2 = Permission.objects.get(content_type=content_type, codename="add_pulsars")
    creator.user_permissions.add(permission)
    creator.user_permissions.add(permission2)
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
    subparsers = parser.add_subparsers(dest='command', required=True, help='Database models which can be interrogated')

    target_parser = subparsers.add_parser(CliTargets.get_name(), help=CliTargets.get_description())
    CliTargets.configure_parsers(target_parser)


@pytest.mark.django_db
def test_cli_target_create_with_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_targets")

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
def test_cli_target_list_with_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = None

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    print(json.loads(response.content))
    assert response.status_code == 200
    assert response.content == b'{"data":{"targets":[]}}'


@pytest.mark.django_db
def test_cli_target_list_with_name_and_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.name = "name"

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    print(json.loads(response.content))
    assert response.status_code == 200
    assert response.content == b'{"data":{"targetsByName":[]}}'


@pytest.mark.django_db
def test_cli_target_list_with_id_and_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = 1
    args.name = None

    t = CliTargets(client, "/graphql/", jwt_token)
    response = t.process(args)
    print(json.loads(response.content))
    assert response.status_code == 200
    # assert response.content == b'{"data":{"targetById":[]}}'


@pytest.mark.django_db
def test_cli_target_update_with_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_targets")

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
    subparsers = parser.add_subparsers(dest='command', required=True, help='Database models which can be interrogated')

    pulsar_parser = subparsers.add_parser(CliPulsars.get_name(), help=CliPulsars.get_description())
    CliPulsars.configure_parsers(pulsar_parser)


@pytest.mark.django_db
def test_cli_pulsar_create_with_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_pulsars")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "create"
    args.jname = "jname"
    args.state = "state"
    args.comment = "comment"

    t = CliPulsars(client, "/graphql/", jwt_token)
    response = t.process(args)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createPulsar":{"pulsar":{"id":"1"}}}}'


@pytest.mark.django_db
def test_cli_pulsar_list_with_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_pulsars")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()
    args.subcommand = "list"
    args.id = None
    args.jname = None

    t = CliPulsars(client, "/graphql/", jwt_token)
    response = t.process(args)
    print(json.loads(response.content))
    assert response.status_code == 200
    assert response.content == b'{"data":{"pulsars":[]}}'


@pytest.mark.django_db
def test_cli_pulsar_update_with_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_pulsars")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    args = __obtain_default_args()

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


def test_graphql_client():
    url = "http://127.0.0.1:8000/graphql"
    verbose = False
    client = GraphQLClient(url, verbose)
    try:
        client.connect()
    except:
        print("Caught connection exception")
