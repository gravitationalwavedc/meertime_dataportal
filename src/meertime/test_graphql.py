import pytest
import json
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

from dataportal.models import (
    Basebandings,
    Collections,
    Ephemerides,
    Filterbankings,
    Foldings,
    Instrumentconfigs,
    Launches,
    Observations,
    Calibrations,
    Pipelineimages,
    Pipelines,
    Processingcollections,
    Processings,
    Projects,
    Pulsaraliases,
    Pulsartargets,
    Pulsars,
    Rfis,
    Targets,
    Telescopes,
    Templates,
    Toas,
)

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


# Test querying

# pulsars query
query_target = """
    query {
        targets {
            name
        }
    }
"""


def __create_target():
    target = Targets.objects.create(name="J1234-5678", raj="12:34:00", decj="-56:78:00")
    return target


@pytest.mark.django_db
def test_graphql_targets_query_no_token(client, django_user_model):
    target = __create_target()
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":9}],"path":["targets"]}],"data":{"targets":null}}'
    response = client.post("/graphql/", {"query": query_target})
    assert response.content == expected
    assert response.status_code == 200


@pytest.mark.django_db
def test_graphql_targets_query_with_token(client, django_user_model):
    user = __create_viewer(client, django_user_model)
    target = __create_target()
    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)
    # try mutation with the token
    payload = {"query": query_target}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)

    expected = b'{"data":{"targets":[{"name":"J1234-5678"}]}}'
    assert response.content == expected
    assert response.status_code == 200


mutation_target = """
mutation ($name: String!, $raj: String!, $decj: String!) {
  createTarget(name: $name, raj: $raj, decj: $decj) {
    target {
      name,      
    }
  }
}
"""

mutation_target_vars = """
{
    "name": "J0437-4715",
    "raj": "04:37:00",
    "decj": "-47:15:00"
}
"""


@pytest.mark.django_db
def test_graphql_createTarget_with_token(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_targets")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)

    payload = {"query": mutation_target, "variables": mutation_target_vars}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)

    assert response.status_code == 200
    assert response.content == b'{"data":{"createTarget":{"target":{"name":"J0437-4715"}}}}'


@pytest.mark.django_db
def test_graphql_createTarget_with_token_without_permission(client, django_user_model):
    user = __create_viewer(client, django_user_model)

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)

    payload = {"query": mutation_target, "variables": mutation_target_vars}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    error_list = json.loads(response.content)["errors"]

    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":3}],"path":["createTarget"]}],"data":{"createTarget":null}}'

    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_createTarget_without_token(client, django_user_model):
    payload = {"query": mutation_target, "variables": mutation_target_vars}
    response = client.post("/graphql/", payload)
    error_list = json.loads(response.content)["errors"]

    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":3}],"path":["createTarget"]}],"data":{"createTarget":null}}'

    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected
