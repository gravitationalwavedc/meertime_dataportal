import pytest
import json
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# need to modify the sys path to get the imports of cli tables working
import sys

sys.path.append("cli")

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


@pytest.fixture
def args():
    class Struct(object):
        pass

    args = Struct()
    args.subcommand = None
    args.verbose = False
    args.very_verbose = False
    return args


jwt_vars_creator = """
    {
        "username": "creator",
        "password":  "rotaerc"
    }
"""


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


@pytest.fixture
def jwt_token(client):
    # obtain the token
    payload = {"query": jwt_mutation, "variables": jwt_vars_creator}
    response = client.post("/graphql/", payload)
    data = json.loads(response.content)["data"]
    jwt_token = data["tokenAuth"]["token"]
    return jwt_token


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
