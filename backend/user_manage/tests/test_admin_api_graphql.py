import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient
from utils.constants import UserRole


User = get_user_model()


def create_admin_user():
    client = JSONWebTokenClient()
    user = User.objects.create(username="adminuser", role=UserRole.ADMIN.value)
    return client, user


def create_non_admin_user():
    client = JSONWebTokenClient()
    user = User.objects.create(username="nonadminuser", role=UserRole.UNRESTRICTED.value)
    return client, user


@pytest.mark.django_db
def test_create_provisional_user_no_token():
    client, user = create_admin_user()

    query = \
        """
          mutation CreateProvisionalUser($email: String!, $role: String!) {
            createProvisionalUser(email: $email, role: $role) {
              ok,
              emailSent,
              errors,
            }
          }
        """

    variables = {
        'email': 'shiblicse@gmail.com',
        'role': 'unrestricted',
    }

    response = client.execute(
        query=query, variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_create_provisional_user_with_token():
    client, user = create_admin_user()
    client.authenticate(user)

    query = \
        """
          mutation CreateProvisionalUser($email: String!, $role: String!) {
            createProvisionalUser(email: $email, role: $role) {
              ok,
              emailSent,
              errors,
            }
          }
        """

    variables = {
        'email': 'shiblicse@gmail.com',
        'role': 'unrestricted',
    }

    expected = {
        'createProvisionalUser': {
            'ok': True,
            'emailSent': True,
            'errors': None,
        }
    }

    response = client.execute(
        query=query, variables=variables,
    )

    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_create_provisional_user_unauthorized():
    client, user = create_non_admin_user()
    client.authenticate(user)

    query = \
        """
          mutation CreateProvisionalUser($email: String!, $role: String!) {
            createProvisionalUser(email: $email, role: $role) {
              ok,
              emailSent,
              errors,
            }
          }
        """

    variables = {
        'email': 'shiblicse@gmail.com',
        'role': 'unrestricted',
    }

    expected = 'You do not have permission to perform this action'

    response = client.execute(
        query=query, variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected


@pytest.mark.django_db
def test_delete_user_no_token():
    client, user = create_admin_user()

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation DeleteUser($username: String!) {
            deleteUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    response = client.execute(
        query=query, variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_delete_user_with_token():
    client, user = create_admin_user()
    client.authenticate(user)

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation DeleteUser($username: String!) {
            deleteUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    expected = {
        'deleteUser': {
            'ok': True,
            'errors': None,
        }
    }

    response = client.execute(
        query=query, variables=variables,
    )

    assert not response.errors
    assert response.data == expected
    assert not User.objects.filter(username=user.username).exists()


@pytest.mark.django_db
def test_delete_user_unauthorized():
    client, user = create_non_admin_user()
    client.authenticate(user)

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation DeleteUser($username: String!) {
            deleteUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    expected = 'You do not have permission to perform this action'

    response = client.execute(
        query=query, variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected


@pytest.mark.django_db
def test_deactivate_user_no_token():
    client, user = create_admin_user()

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation DeactivateUser($username: String!) {
            deactivateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    response = client.execute(
        query=query, variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_deactivate_user_with_token():
    client, user = create_admin_user()
    client.authenticate(user)

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation DeactivateUser($username: String!) {
            deactivateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    expected = {
        'deactivateUser': {
            'ok': True,
            'errors': None,
        }
    }

    response = client.execute(
        query=query, variables=variables,
    )

    assert not response.errors
    assert response.data == expected
    assert not User.objects.get(username=user.username).is_active


@pytest.mark.django_db
def test_activate_user_unauthorized():
    client, user = create_non_admin_user()
    client.authenticate(user)

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation ActivateUser($username: String!) {
            activateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    expected = 'You do not have permission to perform this action'

    response = client.execute(
        query=query, variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected


@pytest.mark.django_db
def test_activate_user_no_token():
    client, user = create_admin_user()

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation ActivateUser($username: String!) {
            activateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    response = client.execute(
        query=query, variables=variables,
    )
    expected_error_message = "'AnonymousUser' object has no attribute 'role'"
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_activate_user_with_token():
    client, user = create_admin_user()
    client.authenticate(user)

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation ActivateUser($username: String!) {
            activateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    expected = {
        'activateUser': {
            'ok': True,
            'errors': None,
        }
    }

    response = client.execute(
        query=query, variables=variables,
    )

    assert not response.errors
    assert response.data == expected
    assert User.objects.get(username=user.username).is_active


@pytest.mark.django_db
def test_deactivate_user_unauthorized():
    client, user = create_non_admin_user()
    client.authenticate(user)

    user = User.objects.create(
        username='myuser@myuser.com',
        email='myuser@myuser.com',
    )

    query = \
        """
          mutation DeactivateUser($username: String!) {
            deactivateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

    variables = {
        'username': user.username,
    }

    expected = 'You do not have permission to perform this action'

    response = client.execute(
        query=query, variables=variables,
    )

    assert response.errors
    assert response.errors[0].message == expected
