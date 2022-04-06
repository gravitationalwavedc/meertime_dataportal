import json
import datetime
from unittest.mock import patch

from django.core import mail
from django.utils import timezone
from graphene_django.utils.testing import GraphQLTestCase

from django.contrib.auth import get_user_model
from ..models import Registration, PasswordResetRequest

UserModel = get_user_model()


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


class PasswordResetRequestTestCase(GraphQLTestCase):

    def setUp(self) -> None:
        self.user_details = dict({
            'username': 'test@test.com',
            'email': 'test@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'test@password',
        })
        UserModel.objects.create_user(**self.user_details)

    def test_create_password_reset_request(self):
        response = self.query(
            '''
            mutation PasswordResetRequestMutation($email: String!) {
                createPasswordResetRequest(email: $email)
                {
                    ok,
                    passwordResetRequest {
                        id,
                        verificationExpiry,
                    },
                    errors,
                }
            }
            ''',
            op_name='PasswordResetRequestMutation',
            variables={
                'email': 'test@test.com',
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content['data']['createPasswordResetRequest']['ok'])
        self.assertIsNotNone(content['data']['createPasswordResetRequest']['passwordResetRequest'])
        self.assertIsNotNone(
            content['data']['createPasswordResetRequest']['passwordResetRequest']['verificationExpiry'])
        self.assertEqual(mail.outbox[0].subject, "Your password reset code for Meertime account.")

    def test_create_password_reset_request_no_email(self):
        response = self.query(
            '''
            mutation PasswordResetRequestMutation($email: String!) {
                createPasswordResetRequest(email: $email)
                {
                    ok,
                    passwordResetRequest {
                        id,
                        verificationExpiry,
                    },
                    errors,
                }
            }
            ''',
            op_name='PasswordResetRequestMutation',
            variables={
                'email': 'doesnotexist@test.com',
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content['data']['createPasswordResetRequest']['ok'])
        self.assertIsNotNone(content['data']['createPasswordResetRequest']['passwordResetRequest'])
        self.assertIsNotNone(
            content['data']['createPasswordResetRequest']['passwordResetRequest']['verificationExpiry'])
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetTestCase(GraphQLTestCase):

    def setUp(self) -> None:
        self.user_details = dict({
            'username': 'test@test.com',
            'email': 'test@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'test@password',
        })
        self.user = UserModel.objects.create_user(**self.user_details)

        # create password reset request
        self.prr = PasswordResetRequest.objects.create(email=self.user_details.get('email'))
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        self.new_password = 'Abcdefgh#123'

    def test_password_reset(self):
        response = self.query(
            '''
            mutation PasswordResetMutation($verification_code: String!, $password: String!) {
               passwordReset(verificationCode: $verification_code, password: $password)
                {
                    ok,
                    passwordResetRequest {
                        id,
                        status,
                    },
                    errors,
                }
            }
            ''',
            op_name='PasswordResetMutation',
            variables={
                'verification_code': f'{self.prr.verification_code}',
                'password': self.new_password,
            }
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content['data']['passwordReset']['ok'])
        self.assertIsNotNone(content['data']['passwordReset']['passwordResetRequest'])
        self.assertEqual(content['data']['passwordReset']['passwordResetRequest']['status'],
                         PasswordResetRequest.UPDATED)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

    def test_password_reset_invalid_verification_code(self):
        response = self.query(
            '''
            mutation PasswordResetMutation($verification_code: String!, $password: String!) {
               passwordReset(verificationCode: $verification_code, password: $password)
                {
                    ok,
                    passwordResetRequest {
                        id,
                        status,
                    },
                    errors,
                }
            }
            ''',
            op_name='PasswordResetMutation',
            variables={
                'verification_code': 'invalid_uuid_code',
                'password': self.new_password,
            }
        )

        content = json.loads(response.content)

        self.assertFalse(content['data']['passwordReset']['ok'])
        self.assertIsNone(content['data']['passwordReset']['passwordResetRequest'])
        self.assertIsNotNone(content['data']['passwordReset']['errors'])
        self.assertEqual(content['data']['passwordReset']['errors'][0], 'Invalid verification code.')

    def test_password_reset_verification_used(self):
        user_details = dict({
            'username': 'testing@test.com',
            'email': 'testing@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'testing@password',
        })
        UserModel.objects.create_user(**user_details)

        # create password reset request
        prr = PasswordResetRequest.objects.create(email=user_details.get('email'))
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        new_password = 'Abcdefgh#123'

        prr.status = PasswordResetRequest.UPDATED
        prr.save()

        response = self.query(
            '''
            mutation PasswordResetMutation($verification_code: String!, $password: String!) {
               passwordReset(verificationCode: $verification_code, password: $password)
                {
                    ok,
                    passwordResetRequest {
                        id,
                        status,
                    },
                    errors,
                }
            }
            ''',
            op_name='PasswordResetMutation',
            variables={
                'verification_code': f'{prr.verification_code}',
                'password': new_password,
            }
        )

        content = json.loads(response.content)

        self.assertFalse(content['data']['passwordReset']['ok'])
        self.assertIsNone(content['data']['passwordReset']['passwordResetRequest'])
        self.assertIsNotNone(content['data']['passwordReset']['errors'])
        self.assertEqual(content['data']['passwordReset']['errors'][0], 'The verification code has been used.')

    def test_password_reset_verification_user_not_found(self):
        user_details = dict({
            'username': 'testing@test.com',
            'email': 'testing@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'testing@password',
        })
        user = UserModel.objects.create_user(**user_details)

        # create password reset request
        prr = PasswordResetRequest.objects.create(email=user_details.get('email'))
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        new_password = 'Abcdefgh#123'

        user.delete()

        response = self.query(
            '''
            mutation PasswordResetMutation($verification_code: String!, $password: String!) {
               passwordReset(verificationCode: $verification_code, password: $password)
                {
                    ok,
                    passwordResetRequest {
                        id,
                        status,
                    },
                    errors,
                }
            }
            ''',
            op_name='PasswordResetMutation',
            variables={
                'verification_code': f'{prr.verification_code}',
                'password': new_password,
            }
        )

        content = json.loads(response.content)

        self.assertFalse(content['data']['passwordReset']['ok'])
        self.assertIsNone(content['data']['passwordReset']['passwordResetRequest'])
        self.assertIsNotNone(content['data']['passwordReset']['errors'])
        self.assertEqual(content['data']['passwordReset']['errors'][0],
                         'No user found. Please contact support regarding this.')

    def test_password_reset_verification_verification_code_does_not_exist(self):
        user_details = dict({
            'username': 'testing@test.com',
            'email': 'testing@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'testing@password',
        })
        UserModel.objects.create_user(**user_details)

        # create password reset request
        prr = PasswordResetRequest.objects.create(email=user_details.get('email'))
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        new_password = 'Abcdefgh#123'

        prr.delete()

        response = self.query(
            '''
            mutation PasswordResetMutation($verification_code: String!, $password: String!) {
               passwordReset(verificationCode: $verification_code, password: $password)
                {
                    ok,
                    passwordResetRequest {
                        id,
                        status,
                    },
                    errors,
                }
            }
            ''',
            op_name='PasswordResetMutation',
            variables={
                'verification_code': f'{prr.verification_code}',
                'password': new_password,
            }
        )

        content = json.loads(response.content)

        self.assertFalse(content['data']['passwordReset']['ok'])
        self.assertIsNone(content['data']['passwordReset']['passwordResetRequest'])
        self.assertIsNotNone(content['data']['passwordReset']['errors'])
        self.assertEqual(content['data']['passwordReset']['errors'][0], 'Verification code does not exist.')
