"""
Integration tests for Bearer token authentication
Tests the complete flow from HTTP request to GraphQL resolution
"""

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from user_manage.models import ApiToken
from utils.constants import UserRole

User = get_user_model()


class BearerTokenIntegrationTestCase(TestCase):
    """Integration tests for Bearer token authentication with HTTP requests"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
            role=UserRole.UNRESTRICTED.value,
        )
        self.token = ApiToken.objects.create(
            user=self.user, name="Integration Test Token", key="integration_test_token_123456789"
        )

    def test_bearer_token_graphql_request(self):
        """Test Bearer token authentication with GraphQL request"""

        # GraphQL query to test authentication
        graphql_query = {
            "query": """
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
                        tokenValue
                        errors
                    }
                }
            """,
            "variables": {"input": {"name": "New Token via Bearer Auth"}},
        }

        # Make request with Bearer token
        response = self.client.post(
            reverse("graphql"),
            data=json.dumps(graphql_query),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertNotIn("errors", response_data)

        create_token_data = response_data["data"]["createApiToken"]
        self.assertTrue(create_token_data["ok"])
        self.assertEqual(create_token_data["token"]["name"], "New Token via Bearer Auth")
        self.assertIsNotNone(create_token_data["token"])
        self.assertIsNotNone(create_token_data["tokenValue"])

    def test_bearer_token_invalid_token(self):
        """Test that invalid Bearer token returns proper error"""

        graphql_query = {
            "query": """
                mutation CreateApiTokenMutation($input: CreateApiTokenInput!) {
                    createApiToken(input: $input) {
                        ok
                        token {
                            id
                            name
                            preview
                            created
                        }
                        tokenValue
                        errors
                    }
                }
            """,
            "variables": {"input": {"name": "Should Fail"}},
        }

        # Make request with invalid Bearer token
        response = self.client.post(
            reverse("graphql"),
            data=json.dumps(graphql_query),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer invalid_token_123",
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        # Should have authentication errors since mutation requires login
        self.assertIn("errors", response_data)

    def test_bearer_token_no_auth_header(self):
        """Test request without Authorization header"""

        graphql_query = {
            "query": """
                mutation CreateApiTokenMutation($input: CreateApiTokenInput!) {
                    createApiToken(input: $input) {
                        ok
                        token {
                            id
                            name
                            preview
                            created
                        }
                        tokenValue
                        errors
                    }
                }
            """,
            "variables": {"input": {"name": "Should Fail"}},
        }

        # Make request without Authorization header
        response = self.client.post(
            reverse("graphql"), data=json.dumps(graphql_query), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        # Should have authentication errors since mutation requires login
        self.assertIn("errors", response_data)

    def test_bearer_token_list_tokens(self):
        """Test listing tokens with Bearer authentication"""

        # Create additional tokens for the user
        ApiToken.objects.create(user=self.user, name="Token 1", key="key1_123456789")
        ApiToken.objects.create(user=self.user, name="Token 2", key="key2_123456789")

        graphql_query = {
            "query": """
                query ApiTokensQuery {
                    apiTokens {
                        edges {
                            node {
                                id
                                name
                                preview
                                created
                                lastUsed
                                isActive
                            }
                        }
                    }
                }
            """
        }

        response = self.client.post(
            reverse("graphql"),
            data=json.dumps(graphql_query),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token.key}",
        )

        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertNotIn("errors", response_data)

        tokens_data = response_data["data"]["apiTokens"]["edges"]
        self.assertEqual(len(tokens_data), 3)  # Original + 2 new tokens
        token_names = [edge["node"]["name"] for edge in tokens_data]
        self.assertIn("Integration Test Token", token_names)
        self.assertIn("Token 1", token_names)
        self.assertIn("Token 2", token_names)
