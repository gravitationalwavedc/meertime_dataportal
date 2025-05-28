import json
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.db import IntegrityError
from graphene_django.utils.testing import GraphQLTestCase
from graphql_relay import to_global_id

from user_manage.models import ApiToken
from user_manage.backends import BearerTokenAuthentication
from utils.constants import UserRole

User = get_user_model()


class BearerTokenAuthenticationTestCase(TestCase):
    """Test cases for Bearer token authentication"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
            role=UserRole.UNRESTRICTED.value,
        )
        self.token = ApiToken.objects.create(user=self.user, name="Test Token", key="test_token_key_123456789")

    def test_bearer_token_authentication(self):
        """Test that Bearer token authentication works"""
        backend = BearerTokenAuthentication()

        # Create a mock request object
        class MockRequest:
            pass

        request = MockRequest()

        # Test valid token
        authenticated_user = backend.authenticate(request, token="test_token_key_123456789")
        self.assertEqual(authenticated_user, self.user)

        # Test invalid token
        invalid_user = backend.authenticate(request, token="invalid_token")
        self.assertIsNone(invalid_user)

        # Test expired token
        self.token.is_active = False
        self.token.save()
        expired_user = backend.authenticate(request, token="test_token_key_123456789")
        self.assertIsNone(expired_user)

    def test_token_default_expiry(self):
        """Test that new tokens get a default expiry based on configured days"""
        # Create a new token
        new_token = ApiToken.objects.create(user=self.user, name="Test Token with Default Expiry")

        # Check that expires_at is set to approximately the configured days from now
        expected_expiry = timezone.now() + timedelta(days=settings.API_TOKEN_DEFAULT_EXPIRY_DAYS)
        self.assertIsNotNone(new_token.expires_at)

        # Allow for a small time difference (within 1 minute) for test execution time
        time_diff = abs((new_token.expires_at - expected_expiry).total_seconds())
        self.assertLess(
            time_diff,
            60,
            f"Expiry should be within 1 minute of expected {settings.API_TOKEN_DEFAULT_EXPIRY_DAYS}-day expiry",
        )

    def test_token_expires_at_none_means_never_expires(self):
        """Test that tokens with expires_at=None never expire"""
        # Create a token with no expiry
        never_expires_token = ApiToken.objects.create(user=self.user, name="Never Expires Token", expires_at=None)

        self.assertFalse(never_expires_token.is_expired())

    def test_token_expiry_authentication(self):
        """Test that expired tokens cannot authenticate"""
        # Create a token that expired yesterday
        expired_token = ApiToken.objects.create(
            user=self.user, name="Expired Token", expires_at=timezone.now() - timedelta(days=1)
        )

        backend = BearerTokenAuthentication()

        class MockRequest:
            pass

        request = MockRequest()

        # Test that expired token fails authentication
        authenticated_user = backend.authenticate(request, token=expired_token.key)
        self.assertIsNone(authenticated_user)

    def test_token_not_yet_expired_authentication(self):
        """Test that tokens not yet expired can authenticate"""
        # Create a token that expires tomorrow
        future_token = ApiToken.objects.create(
            user=self.user, name="Future Token", expires_at=timezone.now() + timedelta(days=1)
        )

        backend = BearerTokenAuthentication()

        class MockRequest:
            pass

        request = MockRequest()

        # Test that future token works
        authenticated_user = backend.authenticate(request, token=future_token.key)
        self.assertEqual(authenticated_user, self.user)


class ApiTokenGraphQLTestCase(GraphQLTestCase):
    """Test cases for API token GraphQL mutations"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
            role=UserRole.UNRESTRICTED.value,
        )

    def test_create_api_token_mutation(self):
        """Test creating an API token via GraphQL"""
        self.client.force_login(self.user)

        response = self.query(
            """
            mutation CreateApiTokenMutation($input: CreateApiTokenInput!) {
                createApiToken(input: $input) {
                    ok
                    token {
                        id
                        name
                        preview
                        created
                        lastUsed
                        expiresAt
                        isActive
                    }
                    errors
                }
            }
            """,
            variables={"input": {"name": "Test API Token"}},
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)

        self.assertTrue(content["data"]["createApiToken"]["ok"])
        self.assertIsNotNone(content["data"]["createApiToken"]["token"])
        self.assertEqual(content["data"]["createApiToken"]["token"]["name"], "Test API Token")

    def test_list_api_tokens_mutation(self):
        """Test listing user's API tokens via GraphQL"""
        # Create some tokens
        ApiToken.objects.create(user=self.user, name="Token 1", key="key1")
        ApiToken.objects.create(user=self.user, name="Token 2", key="key2")

        self.client.force_login(self.user)

        response = self.query(
            """
            query ApiTokensQuery {
                apiTokens {
                    edges {
                        node {
                            id
                            name
                            preview
                            created
                            lastUsed
                            expiresAt
                            isActive
                        }
                    }
                }
            }
            """
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)

        tokens_data = content["data"]["apiTokens"]
        self.assertEqual(len(tokens_data["edges"]), 2)
        token_names = [edge["node"]["name"] for edge in tokens_data["edges"]]
        self.assertIn("Token 1", token_names)
        self.assertIn("Token 2", token_names)

    def test_delete_api_token_mutation(self):
        """Test deleting an API token via GraphQL"""
        token = ApiToken.objects.create(user=self.user, name="Test Token", key="test_key_123456789")

        self.client.force_login(self.user)

        # Create a Relay Global ID for the token
        token_global_id = to_global_id("ApiTokenNode", token.id)

        response = self.query(
            """
            mutation DeleteApiTokenMutation($input: DeleteApiTokenInput!) {
                deleteApiToken(input: $input) {
                    ok
                    errors
                }
            }
            """,
            variables={"input": {"tokenId": token_global_id}},
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)

        self.assertTrue(content["data"]["deleteApiToken"]["ok"])
        self.assertFalse(ApiToken.objects.filter(id=token.id).exists())

    def test_list_api_tokens_includes_expiry(self):
        """Test that listing API tokens includes expiry information"""
        # Create tokens with different expiry scenarios
        never_expires_token = ApiToken.objects.create(
            user=self.user,
            name="Never Expires",
        )
        never_expires_token.expires_at = None
        never_expires_token.save()

        expires_token = ApiToken.objects.create(
            user=self.user, name="Expires Soon", expires_at=timezone.now() + timedelta(days=30)
        )

        self.client.force_login(self.user)

        response = self.query(
            """
            query ApiTokensQuery {
                apiTokens {
                    edges {
                        node {
                            id
                            name
                            preview
                            created
                            lastUsed
                            expiresAt
                            isActive
                        }
                    }
                }
            }
            """
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)

        tokens_data = content["data"]["apiTokens"]["edges"]
        self.assertEqual(len(tokens_data), 2)

        # Find tokens by name and check expiry
        token_nodes = [edge["node"] for edge in tokens_data]
        never_expires_data = next(token for token in token_nodes if token["name"] == "Never Expires")
        expires_data = next(token for token in token_nodes if token["name"] == "Expires Soon")

        self.assertIsNone(never_expires_data["expiresAt"])
        self.assertIsNotNone(expires_data["expiresAt"])

    def test_api_token_unique_constraint_validation(self):
        """Test that token names must be unique per user using the model directly"""
        # Create first token
        first_token = ApiToken.objects.create(user=self.user, name="Unique Test Token")
        self.assertEqual(first_token.name, "Unique Test Token")

        # Creating a second token with the same name should raise IntegrityError
        with self.assertRaises(IntegrityError):
            ApiToken.objects.create(user=self.user, name="Unique Test Token")
