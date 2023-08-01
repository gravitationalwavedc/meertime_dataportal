import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient
from utils.constants import UserRole


User = get_user_model()


@pytest.fixture
def create_users():
    client = JSONWebTokenClient()
    admin = User.objects.create(username="adminuser", email="a@test.com", role=UserRole.ADMIN.value)
    unrestricted = User.objects.create(username="nonadminuser", email="u@test.com", role=UserRole.UNRESTRICTED.value)
    my_user = User.objects.create(username="myuser@myuser.com", email="myuser@myuser.com")
    return client, admin, unrestricted, my_user


@pytest.fixture
def queries():
    create_provisional_user = """
          mutation CreateProvisionalUser($email: String!, $role: String!) {
            createProvisionalUser(email: $email, role: $role) {
              ok,
              emailSent,
              errors,
            }
          }
        """

    delete_user = """
          mutation DeleteUser($username: String!) {
            deleteUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    deactivate_user = """
          mutation DeactivateUser($username: String!) {
            deactivateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    activate_user = """
          mutation ActivateUser($username: String!) {
            activateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    update_role = """
          mutation UpdateRole($username: String!, $role: String!) {
            updateRole(username: $username, role: $role) {
              ok,
              errors,
            }
          }
        """

    return {
        "create_provisional_user": create_provisional_user,
        "delete_user": delete_user,
        "deactivate_user": deactivate_user,
        "activate_user": activate_user,
        "update_role": update_role,
    }


@pytest.mark.django_db
def test_create_provisional_user_no_token(create_users, queries):
    client, user, _, _ = create_users

    query = queries.get("create_provisional_user")

    variables = {
        "email": "shiblicse@gmail.com",
        "role": "unrestricted",
    }

    response = client.execute(
        query=query,
        variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_create_provisional_user_with_token(create_users, queries):
    client, user, _, _ = create_users
    client.authenticate(user)

    query = queries.get("create_provisional_user")

    variables = {
        "email": "shiblicse@gmail.com",
        "role": "unrestricted",
    }

    expected = {
        "createProvisionalUser": {
            "ok": True,
            "emailSent": True,
            "errors": None,
        }
    }

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_create_provisional_user_unauthorized(create_users, queries):
    client, _, user, _ = create_users
    client.authenticate(user)

    query = queries.get("create_provisional_user")

    variables = {
        "email": "shiblicse@gmail.com",
        "role": "unrestricted",
    }

    expected = "You do not have permission to perform this action"

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected


@pytest.mark.django_db
def test_delete_user_no_token(create_users, queries):
    client, user, _, my_user = create_users

    query = queries.get("delete_user")

    variables = {
        "username": my_user.username,
    }

    response = client.execute(
        query=query,
        variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_delete_user_with_token(create_users, queries):
    client, user, _, my_user = create_users
    client.authenticate(user)

    query = queries.get("delete_user")

    variables = {
        "username": my_user.username,
    }

    expected = {
        "deleteUser": {
            "ok": True,
            "errors": None,
        }
    }

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert not response.errors
    assert response.data == expected
    assert not User.objects.filter(username=my_user.username).exists()


@pytest.mark.django_db
def test_delete_user_unauthorized(create_users, queries):
    client, _, user, my_user = create_users
    client.authenticate(user)

    query = queries.get("delete_user")

    variables = {
        "username": my_user.username,
    }

    expected = "You do not have permission to perform this action"

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected


@pytest.mark.django_db
def test_deactivate_user_no_token(create_users, queries):
    client, user, _, my_user = create_users

    query = queries.get("deactivate_user")

    variables = {
        "username": my_user.username,
    }

    response = client.execute(
        query=query,
        variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_deactivate_user_with_token(create_users, queries):
    client, user, _, my_user = create_users
    client.authenticate(user)

    query = queries.get("deactivate_user")

    variables = {
        "username": my_user.username,
    }

    expected = {
        "deactivateUser": {
            "ok": True,
            "errors": None,
        }
    }

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert not response.errors
    assert response.data == expected
    assert not User.objects.get(username=my_user.username).is_active


@pytest.mark.django_db
def test_deactivate_user_unauthorized(create_users, queries):
    client, _, user, my_user = create_users
    client.authenticate(user)

    query = queries.get("deactivate_user")

    variables = {
        "username": my_user.username,
    }

    expected = "You do not have permission to perform this action"

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected


@pytest.mark.django_db
def test_activate_user_no_token(create_users, queries):
    client, user, _, my_user = create_users

    query = queries.get("activate_user")

    variables = {
        "username": my_user.username,
    }

    response = client.execute(
        query=query,
        variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_activate_user_with_token(create_users, queries):
    client, user, _, my_user = create_users
    client.authenticate(user)

    query = queries.get("activate_user")

    variables = {
        "username": my_user.username,
    }

    expected = {
        "activateUser": {
            "ok": True,
            "errors": None,
        }
    }

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert not response.errors
    assert response.data == expected
    assert User.objects.get(username=my_user.username).is_active


@pytest.mark.django_db
def test_activate_user_unauthorized(create_users, queries):
    client, _, user, my_user = create_users
    client.authenticate(user)

    query = queries.get("activate_user")

    variables = {
        "username": my_user.username,
    }

    expected = "You do not have permission to perform this action"

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected


@pytest.mark.django_db
def test_update_role_no_token(create_users, queries):
    client, user, _, my_user = create_users

    query = queries.get("update_role")

    variables = {
        "username": my_user.username,
        "role": "unrestricted",
    }

    response = client.execute(
        query=query,
        variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_update_role_with_token(create_users, queries):
    client, user, _, my_user = create_users
    client.authenticate(user)

    query = queries.get("update_role")

    variables = {
        "username": my_user.username,
        "role": "unrestricted",
    }

    expected = {
        "updateRole": {
            "ok": True,
            "errors": None,
        }
    }

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert not response.errors
    assert response.data == expected
    assert User.objects.get(username=my_user.username).role == UserRole.UNRESTRICTED.value


@pytest.mark.django_db
def test_update_role_unauthorized(create_users, queries):
    client, _, user, my_user = create_users
    client.authenticate(user)

    query = queries.get("update_role")

    variables = {
        "username": my_user.username,
        "role": "unrestricted",
    }

    expected = "You do not have permission to perform this action"

    response = client.execute(
        query=query,
        variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected
