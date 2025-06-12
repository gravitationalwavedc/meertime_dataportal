import json

from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase

from utils.constants import UserRole

User = get_user_model()


class AdminUserGraphQLTestCase(GraphQLTestCase):
    """Test cases for Admin user GraphQL mutations"""

    def setUp(self):
        # Create test users
        self.admin = User.objects.create(username="adminuser", email="a@test.com", role=UserRole.ADMIN.value)
        self.unrestricted = User.objects.create(
            username="nonadminuser", email="u@test.com", role=UserRole.UNRESTRICTED.value
        )
        self.my_user = User.objects.create(username="myuser@myuser.com", email="myuser@myuser.com")

        # Define GraphQL queries
        self.create_provisional_user = """
          mutation CreateProvisionalUser($email: String!, $role: String!) {
            createProvisionalUser(email: $email, role: $role) {
              ok,
              emailSent,
              errors,
            }
          }
        """

        self.delete_user = """
          mutation DeleteUser($username: String!) {
            deleteUser(username: $username) {
              ok,
              errors,
            }
          }
        """

        self.deactivate_user = """
          mutation DeactivateUser($username: String!) {
            deactivateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

        self.activate_user = """
          mutation ActivateUser($username: String!) {
            activateUser(username: $username) {
              ok,
              errors,
            }
          }
        """

        self.update_role = """
          mutation UpdateRole($username: String!, $role: String!) {
            updateRole(username: $username, role: $role) {
              ok,
              errors,
            }
          }
        """

    def test_create_provisional_user_no_token(self):
        """Test creating provisional user without authentication token fails"""
        variables = {
            "email": "shiblicse@gmail.com",
            "role": "unrestricted",
        }

        response = self.query(
            self.create_provisional_user,
            variables=variables,
        )

        # Parse the response content to a JSON dict
        content = json.loads(response.content)
        self.assertIn("errors", content)
        expected_error_message = "'AnonymousUser' object has no attribute 'role'"
        self.assertEqual(content["errors"][0]["message"], expected_error_message)

    def test_create_provisional_user_with_token(self):
        """Test creating provisional user with admin authentication token succeeds"""
        self.client.force_login(self.admin)

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

        response = self.query(
            self.create_provisional_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertEqual(content["data"], expected)

    def test_create_provisional_user_unauthorized(self):
        """Test creating provisional user with non-admin authentication token fails"""
        self.client.force_login(self.unrestricted)

        variables = {
            "email": "shiblicse@gmail.com",
            "role": "unrestricted",
        }

        expected = "You do not have permission to perform this action"

        response = self.query(
            self.create_provisional_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        self.assertEqual(content["errors"][0]["message"], expected)

    def test_delete_user_no_token(self):
        """Test deleting user without authentication token fails"""
        variables = {
            "username": self.my_user.username,
        }

        response = self.query(
            self.delete_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        expected_error_message = "'AnonymousUser' object has no attribute 'role'"
        self.assertEqual(content["errors"][0]["message"], expected_error_message)

    def test_delete_user_with_token(self):
        """Test deleting user with admin authentication token succeeds"""
        self.client.force_login(self.admin)

        variables = {
            "username": self.my_user.username,
        }

        expected = {
            "deleteUser": {
                "ok": True,
                "errors": None,
            }
        }

        response = self.query(
            self.delete_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertEqual(content["data"], expected)
        self.assertFalse(User.objects.filter(username=self.my_user.username).exists())

    def test_delete_user_unauthorized(self):
        """Test deleting user with non-admin authentication token fails"""
        self.client.force_login(self.unrestricted)

        variables = {
            "username": self.my_user.username,
        }

        expected = "You do not have permission to perform this action"

        response = self.query(
            self.delete_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        self.assertEqual(content["errors"][0]["message"], expected)

    def test_deactivate_user_no_token(self):
        """Test deactivating user without authentication token fails"""
        variables = {
            "username": self.my_user.username,
        }

        response = self.query(
            self.deactivate_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        expected_error_message = "'AnonymousUser' object has no attribute 'role'"
        self.assertEqual(content["errors"][0]["message"], expected_error_message)

    def test_deactivate_user_with_token(self):
        """Test deactivating user with admin authentication token succeeds"""
        self.client.force_login(self.admin)

        variables = {
            "username": self.my_user.username,
        }

        expected = {
            "deactivateUser": {
                "ok": True,
                "errors": None,
            }
        }

        response = self.query(
            self.deactivate_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertEqual(content["data"], expected)
        user = User.objects.get(username=self.my_user.username)
        self.assertFalse(user.is_active)

    def test_deactivate_user_unauthorized(self):
        """Test deactivating user with non-admin authentication token fails"""
        self.client.force_login(self.unrestricted)

        variables = {
            "username": self.my_user.username,
        }

        expected = "You do not have permission to perform this action"

        response = self.query(
            self.deactivate_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        self.assertEqual(content["errors"][0]["message"], expected)

    def test_activate_user_no_token(self):
        """Test activating user without authentication token fails"""
        variables = {
            "username": self.my_user.username,
        }

        response = self.query(
            self.activate_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        expected_error_message = "'AnonymousUser' object has no attribute 'role'"
        self.assertEqual(content["errors"][0]["message"], expected_error_message)

    def test_activate_user_with_token(self):
        """Test activating user with admin authentication token succeeds"""
        self.client.force_login(self.admin)

        # First deactivate the user
        self.my_user.is_active = False
        self.my_user.save()

        variables = {
            "username": self.my_user.username,
        }

        expected = {
            "activateUser": {
                "ok": True,
                "errors": None,
            }
        }

        response = self.query(
            self.activate_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertEqual(content["data"], expected)
        user = User.objects.get(username=self.my_user.username)
        self.assertTrue(user.is_active)

    def test_activate_user_unauthorized(self):
        """Test activating user with non-admin authentication token fails"""
        self.client.force_login(self.unrestricted)

        variables = {
            "username": self.my_user.username,
        }

        expected = "You do not have permission to perform this action"

        response = self.query(
            self.activate_user,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        self.assertEqual(content["errors"][0]["message"], expected)

    def test_update_role_no_token(self):
        """Test updating user role without authentication token fails"""
        variables = {
            "username": self.my_user.username,
            "role": "unrestricted",
        }

        response = self.query(
            self.update_role,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        expected_error_message = "'AnonymousUser' object has no attribute 'role'"
        self.assertEqual(content["errors"][0]["message"], expected_error_message)

    def test_update_role_with_token(self):
        """Test updating user role with admin authentication token succeeds"""
        self.client.force_login(self.admin)

        variables = {
            "username": self.my_user.username,
            "role": "unrestricted",
        }

        expected = {
            "updateRole": {
                "ok": True,
                "errors": None,
            }
        }

        response = self.query(
            self.update_role,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertEqual(content["data"], expected)
        user = User.objects.get(username=self.my_user.username)
        self.assertEqual(user.role, UserRole.UNRESTRICTED.value)

    def test_update_role_unauthorized(self):
        """Test updating user role with non-admin authentication token fails"""
        self.client.force_login(self.unrestricted)

        variables = {
            "username": self.my_user.username,
            "role": "unrestricted",
        }

        expected = "You do not have permission to perform this action"

        response = self.query(
            self.update_role,
            variables=variables,
        )

        content = json.loads(response.content)
        self.assertIn("errors", content)
        self.assertEqual(content["errors"][0]["message"], expected)
