import pytest
import json
from dataportal.models import Observations, Pulsars, Utcs
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from graphql.error.located_error import GraphQLLocatedError
from datetime import datetime


# Auxiliary functions
def __create_viewer(client, django_user_model):
    username = "viewer"
    password = "reweiv"
    viewer = django_user_model.objects.create_user(username=username, password=password)
    return viewer


def __create_creator(client, django_user_model):
    username = "creator"
    password = "rotaerc"
    creator = django_user_model.objects.create_user(username=username, password=password)

    content_type = ContentType.objects.get_for_model(Observations)
    permission = Permission.objects.get(content_type=content_type, codename="add_observations")
    creator.user_permissions.add(permission)
    return creator


def __create_psr_utc_obs():
    psr = Pulsars.objects.create(jname="J1234-5678")
    utc_str = "2000-01-01-12:59:12"
    utc_dt = datetime.strptime(f"{utc_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc = Utcs.objects.create(utc=utc_str, utc_ts=utc_dt)
    Observations.objects.create(pulsar=psr, utc=utc, beam=1)
    return psr, utc


# Test querying
# pulsars query
def test_graphql_pulsars_query_no_login(client, django_user_model):
    psr, _ = __create_psr_utc_obs()
    query = """
        query {
            pulsars {
                jname
            }
        }
    """
    expected = b'{"data":{"pulsars":[{"jname":"J1234-5678"}]}}'
    response = client.post("/graphql/", {"query": query})
    assert response.status_code == 200
    assert "pulsars" in json.loads(response.content)["data"]
    assert json.loads(response.content)["data"]["pulsars"][0]["jname"] == psr.jname
    assert response.content == expected


# utcs query
def test_graphql_utcs_query_no_login(client, django_user_model):
    _, utc = __create_psr_utc_obs()
    query = """
        query {
            utcs {
                utc
            }
        }
    """
    expected = b'{"data":{"utcs":[{"utc":"2000-01-01-12:59:12"}]}}'
    response = client.post("/graphql/", {"query": query})
    assert response.status_code == 200
    assert "utcs" in json.loads(response.content)["data"]
    assert json.loads(response.content)["data"]["utcs"][0]["utc"] == utc.utc
    assert response.content == expected


# observations query:
def test_graphql_observations_query_no_login(client, django_user_model):
    psr, utc = __create_psr_utc_obs()
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
    expected = b'{"data":{"observations":[{"pulsar":{"jname":"J1234-5678"},"utc":{"utc":"2000-01-01-12:59:12"}}]}}'
    response = client.post("/graphql/", {"query": query})
    assert response.status_code == 200
    assert "observations" in json.loads(response.content)["data"]
    assert json.loads(response.content)["data"]["observations"][0]["pulsar"]["jname"] == psr.jname
    assert json.loads(response.content)["data"]["observations"][0]["utc"]["utc"] == utc.utc
    assert response.content == expected


# Test mutations
# Auxiliary strings for testing mutations
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
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":9}],"path":["createObservation"]}],"data":{"createObservation":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_with_token_without_permission(client, django_user_model):
    user = __create_viewer(client, django_user_model)
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
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":9}],"path":["createObservation"]}],"data":{"createObservation":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_with_token_with_permission(client, django_user_model):
    user = __create_creator(client, django_user_model)
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
