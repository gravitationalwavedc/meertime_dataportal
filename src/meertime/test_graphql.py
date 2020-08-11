import pytest
import json
from dataportal.models import Observations
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from graphql.error.located_error import GraphQLLocatedError


def create_viewer(client, django_user_model):
    username = "viewer"
    password = "reweiv"
    viewer = django_user_model.objects.create_user(username=username, password=password)
    return viewer


def create_creator(client, django_user_model):
    username = "creator"
    password = "rotaerc"
    creator = django_user_model.objects.create_user(username=username, password=password)

    content_type = ContentType.objects.get_for_model(Observations)
    permission = Permission.objects.get(content_type=content_type, codename="add_observations")
    creator.user_permissions.add(permission)
    return creator


def test_graphql_query_no_login(client, django_user_model):
    query = """
       query {
           observations {
               pulsar {
                   jname
               }
               utc {
                   utc
               }
           }
       }
   """
    response = client.post("/graphql/", {"query": query})
    assert response.status_code == 200
    assert "observations" in json.loads(response.content)["data"]


# mutations shared between tests below
mutation = """
    mutation ($jname: String!, $utc: String!, $beam: Int!, $DM: Float, $snr: Float, $length: Float, $nchan: Int, $nbin: Int, $nant: Int, $nant_eff: Int, $proposal: String, $bw: Float, $freq: Float) {
        createObservation(jname: $jname, utc: $utc, beam: $beam, DM: $DM, snr: $snr, length: $length, nchan: $nchan, nbin: $nbin, nant: $nant, nantEff: $nant_eff, proposal: $proposal, bw: $bw, frequency: $freq) {
            observations {
                pulsar {
                    jname
                }
            }
        }
    }
"""
mutation_variables = """
    {
        "jname": "J1234-5678",
        "utc": "2020-08-12-01:02:03",
        "beam": 3,
        "DM": 5.3514,
        "snr": 15.231,
        "length": 201.2,
        "nchan": 856,
        "nant": 57,
        "nbin": 1024,
        "nant_eff": 57,
        "proposal": "SCI-20180516-MB-02",
        "bw": 856,
        "freq": 1235.0123
    }
"""

jwt_mutation = """
    mutation TokenAuth($username: String!, $password: String!) {
        tokenAuth(username: $username, password: $password) {
            token
            payload
            refreshExpiresIn
        }
    }
"""


def test_graphql_mutation_without_token(client, django_user_model):
    payload = {"query": mutation, "variables": mutation_variables}
    response = client.post("/graphql/", payload)
    error_list = json.loads(response.content)["errors"]
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"


@pytest.mark.django_db
def test_graphql_mutation_with_token_without_permission(client, django_user_model):
    user = create_viewer(client, django_user_model)
    assert not user.has_perm("dataportal.add_observations")
    jwt_vars = """
        {
            "username": "viewer",
            "password":  "reweiv"
        }
    """
    # obtain the token
    payload = {"query": jwt_mutation, "variables": jwt_vars}
    response = client.post("/graphql/", payload)
    data = json.loads(response.content)["data"]
    jwt_token = data["tokenAuth"]["token"]

    # try mutation with the token
    payload = {"query": mutation, "variables": mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    error_list = json.loads(response.content)["errors"]
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"


@pytest.mark.django_db
def test_graphql_mutation_with_token_with_permission(client, django_user_model):
    user = create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_observations")

    # create_creator(client, django_user_model)
    jwt_vars = """
        {
            "username": "creator",
            "password":  "rotaerc"
        }
    """
    # obtain the token
    payload = {"query": jwt_mutation, "variables": jwt_vars}
    response = client.post("/graphql/", payload)
    data = json.loads(response.content)["data"]
    jwt_token = data["tokenAuth"]["token"]

    # try mutation with the token
    payload = {"query": mutation, "variables": mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createObservation":{"observations":{"pulsar":{"jname":"J1234-5678"}}}}}'
