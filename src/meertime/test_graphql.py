import pytest
import json
from dataportal.models import Observations, Pulsars, Utcs
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime


# Auxiliary functions
jwt_mutation = """
    mutation TokenAuth($username: String!, $password: String!) {
        tokenAuth(username: $username, password: $password) {
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

    content_type = ContentType.objects.get_for_model(Observations)
    permission = Permission.objects.get(content_type=content_type, codename="add_observations")
    creator.user_permissions.add(permission)
    return creator


jwt_vars_creator = """
    {
        "username": "creator",
        "password":  "rotaerc"
    }
"""


def __create_psr_utc_obs():
    psr = Pulsars.objects.create(jname="J1234-5678")
    utc_str = "2000-01-01-12:59:12"
    utc_dt = datetime.strptime(f"{utc_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc = Utcs.objects.create(utc_ts=utc_dt)
    Observations.objects.create(pulsar=psr, utc=utc, beam=1)
    return psr, utc


def __obtain_jwt_token(client, mutation, vars):
    # obtain the token
    payload = {"query": mutation, "variables": vars}
    response = client.post("/graphql/", payload)
    data = json.loads(response.content)["data"]
    jwt_token = data["tokenAuth"]["token"]
    return jwt_token


# Test querying

# pulsars query
query_psr = """
    query {
        pulsars {
            jname
        }
    }
"""


def test_graphql_pulsars_query_no_token(client, django_user_model):
    psr, _ = __create_psr_utc_obs()
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":9}],"path":["pulsars"]}],"data":{"pulsars":null}}'
    response = client.post("/graphql/", {"query": query_psr})
    assert response.content == expected
    assert response.status_code == 200


def test_graphql_pulsars_query_with_token(client, django_user_model):
    user = __create_viewer(client, django_user_model)
    psr, _ = __create_psr_utc_obs()
    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)
    # try mutation with the token
    payload = {"query": query_psr}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)

    expected = b'{"data":{"pulsars":[{"jname":"J1234-5678"}]}}'
    assert response.content == expected
    assert response.status_code == 200


# utcs query
query_utcs = """
    query {
        utcs {
            utcTs
        }
    }
"""


def test_graphql_utcs_query_no_token(client, django_user_model):
    _, utc = __create_psr_utc_obs()
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":9}],"path":["utcs"]}],"data":{"utcs":null}}'
    response = client.post("/graphql/", {"query": query_utcs})
    assert response.status_code == 200
    assert response.content == expected


def test_graphql_utcs_query_with_token(client, django_user_model):
    user = __create_viewer(client, django_user_model)
    psr, _ = __create_psr_utc_obs()
    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)
    # try mutation with the token
    payload = {"query": query_utcs}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)

    expected = b'{"data":{"utcs":[{"utcTs":"2000-01-01T12:59:12+00:00"}]}}'
    assert response.content == expected
    assert response.status_code == 200


# observations query:
query_obs = """
   query {
        observations {
           pulsar {
               jname
           }
           utc {
               utcTs
           }
       }
   }
"""


def test_graphql_observations_query_no_token(client, django_user_model):
    psr, utc = __create_psr_utc_obs()
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":3,"column":9}],"path":["observations"]}],"data":{"observations":null}}'
    response = client.post("/graphql/", {"query": query_obs})
    assert response.status_code == 200
    assert response.content == expected


def test_graphql_observations_query_with_token(client, django_user_model):
    user = __create_viewer(client, django_user_model)
    psr, _ = __create_psr_utc_obs()
    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)
    # try mutation with the token
    payload = {"query": query_obs}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)

    expected = (
        b'{"data":{"observations":[{"pulsar":{"jname":"J1234-5678"},"utc":{"utcTs":"2000-01-01T12:59:12+00:00"}}]}}'
    )
    assert response.content == expected
    assert response.status_code == 200


# Test mutations
# Auxiliary strings for testing mutations
# mutations shared between tests below
createObservation_mutation = """
    mutation (
        $jname: String!, $utc: String!, $beam: Int!, $DM: Float, $snr: Float, $length: Float, $nchan: Int, $nbin: Int,
        $nant: Int, $nant_eff: Int, $proposal: String, $bw: Float, $freq: Float
    ) {
        createObservation(
            jname: $jname, utc: $utc, beam: $beam, DM: $DM, snr: $snr, length: $length, nchan: $nchan, nbin: $nbin,
            nant: $nant, nantEff: $nant_eff, proposal: $proposal, bw: $bw, frequency: $freq
        ) {
            observations {
                pulsar {
                    jname
                }
            }
        }
    }
"""
createObservation_mutation_variables = """
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


def test_graphql_mutation_createObservation_without_token(client, django_user_model):
    payload = {"query": createObservation_mutation, "variables": createObservation_mutation_variables}
    response = client.post("/graphql/", payload)
    error_list = json.loads(response.content)["errors"]
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":6,"column":9}],"path":["createObservation"]}],"data":{"createObservation":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_createObservation_with_token_without_permission(client, django_user_model):
    user = __create_viewer(client, django_user_model)
    assert not user.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)
    # try mutation with the token
    payload = {"query": createObservation_mutation, "variables": createObservation_mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    error_list = json.loads(response.content)["errors"]
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":6,"column":9}],"path":["createObservation"]}],"data":{"createObservation":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_createObservation_with_token_with_permission(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    # try mutation with the token
    payload = {"query": createObservation_mutation, "variables": createObservation_mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createObservation":{"observations":{"pulsar":{"jname":"J1234-5678"}}}}}'


createSearchmode_mutation = """
    mutation (
        $jname: String!, $utc: String!, $beam: Int!, $DM: Float, $RA: String, $DEC: String, $nbit: Int, $nchan: Int,
        $npol: Int, $tsamp: Float, $nant: Int, $nant_eff: Int, $proposal: String, $length: Float, $bw: Float, $freq: Float
    ) {
        createSearchmode(
            jname: $jname, utc: $utc, beam: $beam, RA: $RA, DEC: $DEC, DM: $DM, nbit: $nbit, nchan: $nchan,
            npol: $npol, tsamp: $tsamp, nant: $nant, nantEff: $nant_eff, proposal: $proposal, length: $length, bw: $bw, frequency: $freq
        ) {
            searchmode {
                pulsar {
                    jname
                }
            }
        }
    }
"""
createSearchmode_mutation_variables = """
    {
        "jname": "J1234-5678",
        "utc": "2020-08-12-01:02:03",
        "beam": 3,
        "RA": "12:34:12.345",
        "DEC": "-56:77:56.789",
        "DM": 5.3514,
        "nbit": 8,
        "nchan": 856,
        "npol": 2,
        "tsamp": 0.000064,
        "nant": 57,
        "nant_eff": 54,
        "proposal": "SCI-20180516-MB-02",
        "length": 201.2,
        "bw": 856,
        "freq": 1235.0123
    }
"""


def test_graphql_mutation_createSearchmode_without_token(client, django_user_model):
    payload = {"query": createSearchmode_mutation, "variables": createSearchmode_mutation_variables}
    response = client.post("/graphql/", payload)
    error_list = json.loads(response.content)["errors"]
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":6,"column":9}],"path":["createSearchmode"]}],"data":{"createSearchmode":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_createSearchmode_with_token_without_permission(client, django_user_model):
    user = __create_viewer(client, django_user_model)
    assert not user.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)
    # try mutation with the token
    payload = {"query": createSearchmode_mutation, "variables": createSearchmode_mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    error_list = json.loads(response.content)["errors"]
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":6,"column":9}],"path":["createSearchmode"]}],"data":{"createSearchmode":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_createSearchmode_with_token_with_permission(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    # try mutation with the token
    payload = {"query": createSearchmode_mutation, "variables": createSearchmode_mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createSearchmode":{"searchmode":{"pulsar":{"jname":"J1234-5678"}}}}}'


createFluxcal_mutation = """
    mutation (
        $jname: String!, $utc: String!, $beam: Int!,  $snr: Float, $length: Float, $nbin: Int, $nchan: Int,
        $nant: Int, $nant_eff: Int, $proposal: String, $bw: Float, $freq: Float
    ) {
        createFluxcal(
            jname: $jname, utc: $utc, beam: $beam, snr: $snr, nbin: $nbin, nchan: $nchan, length: $length,
             nant: $nant, nantEff: $nant_eff, proposal: $proposal, bw: $bw, frequency: $freq
        ) {
            fluxcal {
                pulsar {
                    jname
                }
            }
        }
    }
"""
createFluxcal_mutation_variables = """
    {
        "jname": "J1234-5678",
        "utc": "2020-08-12-01:02:03",
        "beam": 3,
        "snr": 15.231,
        "length": 201.2,
        "nchan": 856,
        "nbin": 1024,
        "nant": 57,
        "nant_eff": 54,
        "proposal": "SCI-20180516-MB-02",
        "bw": 856,
        "freq": 1235.0123
    }
"""


def test_graphql_mutation_createFluxcal_without_token(client, django_user_model):
    payload = {"query": createFluxcal_mutation, "variables": createFluxcal_mutation_variables}
    response = client.post("/graphql/", payload)
    error_list = json.loads(response.content)["errors"]
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":6,"column":9}],"path":["createFluxcal"]}],"data":{"createFluxcal":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_createFluxcal_with_token_without_permission(client, django_user_model):
    user = __create_viewer(client, django_user_model)
    assert not user.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_viewer)
    # try mutation with the token
    payload = {"query": createFluxcal_mutation, "variables": createFluxcal_mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    error_list = json.loads(response.content)["errors"]
    expected = b'{"errors":[{"message":"You do not have permission to perform this action","locations":[{"line":6,"column":9}],"path":["createFluxcal"]}],"data":{"createFluxcal":null}}'
    assert response.status_code == 200
    assert len(error_list) > 0
    assert isinstance(error_list[0], dict)
    assert "message" in error_list[0].keys()
    assert error_list[0]["message"] == "You do not have permission to perform this action"
    assert response.content == expected


@pytest.mark.django_db
def test_graphql_mutation_createFluxcal_with_token_with_permission(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    # try mutation with the token
    payload = {"query": createFluxcal_mutation, "variables": createFluxcal_mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createFluxcal":{"fluxcal":{"pulsar":{"jname":"J1234-5678"}}}}}'


createEphemeris_mutation = """
    mutation (
        $jname: String!, $updated_at: String!, $ephemeris: String!,  $comment: String!) {
        createEphemeris(
            jname: $jname, updatedAt: $updated_at, ephemeris: $ephemeris, comment: $comment) {
            ephemeris {
                pulsar {
                    jname
                }
            }
        }
    }
"""
createEphemeris_mutation_variables = """
    {
        "jname": "J1234-5678",
        "comment": "",
        "updated_at": "2020-08-12-01:02:03",
        "ephemeris": "fake"
    }
"""


@pytest.mark.django_db
def test_graphql_mutation_createEphemeris_with_token_with_permission(client, django_user_model):
    user = __create_creator(client, django_user_model)
    assert user.has_perm("dataportal.add_observations")

    jwt_token = __obtain_jwt_token(client, jwt_mutation, jwt_vars_creator)
    # try mutation with the token
    payload = {"query": createEphemeris_mutation, "variables": createEphemeris_mutation_variables}
    header = {"HTTP_AUTHORIZATION": f"JWT {jwt_token}"}
    response = client.post("/graphql/", payload, **header)
    print(response.status_code)
    print(response.content)
    assert response.status_code == 200
    assert response.content == b'{"data":{"createEphemeris":{"ephemeris":{"pulsar":{"jname":"J1234-5678"}}}}}'
