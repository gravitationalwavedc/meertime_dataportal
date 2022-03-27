import json

from graphene_django.utils.testing import GraphQLTestCase

from ..models import Registration


class RegistrationTestCase(GraphQLTestCase):

    def setUp(self) -> None:
        self.user_details = dict({
            'email': 'test@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'test@password',
        })
        Registration.objects.create(**self.user_details)

    def test_create_registration(self):
        response = self.query(
            '''
            mutation RegisterMutation($first_name: String!, $last_name: String!, $email: String!, $password: String!) {
                createRegistration(input: {
                    firstName: $first_name, 
                    lastName: $last_name, 
                    email: $email, 
                    password: $password,
                })
                {
                    ok,
                    registration {
                        id,
                        verificationExpiry,
                    },
                    errors,
                }
            }
            ''',
            op_name='RegisterMutation',
            variables={
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'password': 'Password#123',
                'email': 'test@email.com',
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content['data']['createRegistration']['ok'])
        self.assertIsNotNone(content['data']['createRegistration']['registration'])
        self.assertIsNotNone(content['data']['createRegistration']['registration']['verificationExpiry'])

    def test_create_registration_exists(self):
        response = self.query(
            '''
            mutation RegisterMutation($first_name: String!, $last_name: String!, $email: String!, $password: String!) {
                createRegistration(input: {
                    firstName: $first_name, 
                    lastName: $last_name, 
                    email: $email, 
                    password: $password,
                })
                {
                    ok,
                    registration {
                        id,
                        verificationExpiry,
                    },
                    errors,
                }
            }
            ''',
            op_name='RegisterMutation',
            variables={
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'password': 'Password#123',
                'email': 'test@test.com',
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content['data']['createRegistration']['ok'])
        self.assertIsNone(content['data']['createRegistration']['registration'])
        self.assertIsNotNone(content['data']['createRegistration']['errors'])
        self.assertEqual(
            content['data']['createRegistration']['errors'][0],
            'Registration with this Email already exists.'
        )
