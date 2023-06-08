from django.test import TestCase
from graphene.test import Client
from graphql_jwt.testcases import JSONWebTokenTestCase

from meertime.schema import schema


class CreateUserMutationTest(JSONWebTokenTestCase):
    def setUp(self):
        self.client = Client(schema)

    def test_create_user_mutation(self):
        # Authenticate a user for testing
        self.authenticate_user()

        # Define the mutation query
        mutation = '''
            mutation ($username: String!, $password: String!) {
                createUser(username: $username, password: $password) {
                    user {
                        id
                        username
                    }
                }
            }
        '''

        # Define the variables for the mutation
        variables = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        # Execute the mutation
        response = self.client.execute(mutation, variables=variables)

        # Check the response for success
        self.assertIsNone(response.errors)

        # Check the created user in the response
        user = response.data['createUser']['user']
        self.assertEqual(user['username'], 'testuser')

        # Additional assertions or checks as needed
        # ...

    def authenticate_user(self):
        # Perform authentication logic and set the authorization header
        # Example using django-graphql-jwt's `authenticate` method
        self.user = authenticate(username='testuser', password='testpassword')
        token = jwt_encode(self.user)
        self.client.defaults['HTTP_AUTHORIZATION'] = f'JWT {token}'