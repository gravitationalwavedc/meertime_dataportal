import datetime
import json
from unittest.mock import patch

import pytest
from django.core import mail
from django.utils import timezone
from graphene_django.utils.testing import GraphQLTestCase

from django.contrib.auth import get_user_model, authenticate
from utils.constants import UserRole
from ..models import Registration, PasswordResetRequest, ProvisionalUser

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.enable_signals
class RegistrationTestCase(GraphQLTestCase):
    def setUp(self) -> None:
        self.user_details = dict(
            {
                "email": "test@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "test@password",
            }
        )
        Registration.objects.create(**self.user_details)

    def test_create_registration(self):
        response = self.query(
            """
            mutation RegisterMutation(
                $first_name: String!,
                $last_name: String!,
                $email: String!,
                $password: String!,
                $captcha: String!
            ) {
                createRegistration(input: {
                    firstName: $first_name,
                    lastName: $last_name,
                    email: $email,
                    password: $password,
                    captcha: $captcha
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
            """,
            op_name="RegisterMutation",
            variables={
                "first_name": "First Name",
                "last_name": "Last Name",
                "password": "Password#123",
                "email": "test@email.com",
                "captcha": "mysecretecaptcha",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content["data"]["createRegistration"]["ok"])
        self.assertIsNotNone(content["data"]["createRegistration"]["registration"])
        self.assertIsNotNone(
            content["data"]["createRegistration"]["registration"]["verificationExpiry"]
        )

    def test_create_registration_exists(self):
        response = self.query(
            """
            mutation RegisterMutation(
                $first_name: String!,
                $last_name: String!,
                $email: String!,
                $password: String!
                $captcha: String!
            ) {
                createRegistration(input: {
                    firstName: $first_name,
                    lastName: $last_name,
                    email: $email,
                    password: $password,
                    captcha: $captcha,
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
            """,
            op_name="RegisterMutation",
            variables={
                "first_name": "First Name",
                "last_name": "Last Name",
                "password": "Password#123",
                "email": "test@test.com",
                "captcha": "mysecretecaptcha",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["createRegistration"]["ok"])
        self.assertIsNone(content["data"]["createRegistration"]["registration"])
        self.assertIsNotNone(content["data"]["createRegistration"]["errors"])
        self.assertEqual(
            content["data"]["createRegistration"]["errors"][0],
            "Registration with this Email already exists.",
        )


@pytest.mark.django_db
@pytest.mark.enable_signals
class VerifyRegistrationTestCase(GraphQLTestCase):
    def setUp(self) -> None:
        self.user_details = dict(
            {
                "email": "test@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "test@password",
            }
        )
        self.registration = Registration.objects.create(**self.user_details)

    def test_verify_registration(self):
        response = self.query(
            """
            mutation VerifyRegistrationMutation($verification_code: String!) {
                verifyRegistration(verificationCode: $verification_code)
                {
                    ok,
                    registration {
                        email,
                        status,
                    },
                    errors,
                }
            }
            """,
            op_name="VerifyRegistrationMutation",
            variables={
                "verification_code": f"{self.registration.verification_code}",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content["data"]["verifyRegistration"]["ok"])
        self.assertIsNotNone(content["data"]["verifyRegistration"]["registration"])
        self.assertIsNotNone(
            content["data"]["verifyRegistration"]["registration"]["email"]
        )
        self.assertEqual(
            content["data"]["verifyRegistration"]["registration"]["status"],
            Registration.VERIFIED,
        )

        # check user created and role assigned
        try:
            user = User.objects.get(username=self.registration.email)
            # the user exists
            assert True

            self.assertEqual(user.role, UserRole.RESTRICTED.value)

        except User.DoesNotExist:
            assert False

    def test_verify_registration_invalid_code(self):
        response = self.query(
            """
            mutation VerifyRegistrationMutation($verification_code: String!) {
                verifyRegistration(verificationCode: $verification_code)
                {
                    ok,
                    registration {
                        email,
                        status,
                    },
                    errors,
                }
            }
            """,
            op_name="VerifyRegistrationMutation",
            variables={
                "verification_code": "invalid_code",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["verifyRegistration"]["ok"])
        self.assertIsNone(content["data"]["verifyRegistration"]["registration"])
        self.assertIsNotNone(content["data"]["verifyRegistration"]["errors"])
        self.assertEqual(
            content["data"]["verifyRegistration"]["errors"][0],
            "Invalid verification code.",
        )

    def test_verify_registration_already_verified(self):
        self.registration.status = Registration.VERIFIED
        self.registration.save()

        response = self.query(
            """
            mutation VerifyRegistrationMutation($verification_code: String!) {
                verifyRegistration(verificationCode: $verification_code)
                {
                    ok,
                    registration {
                        email,
                        status,
                    },
                    errors,
                }
            }
            """,
            op_name="VerifyRegistrationMutation",
            variables={
                "verification_code": f"{self.registration.verification_code}",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["verifyRegistration"]["ok"])
        self.assertIsNone(content["data"]["verifyRegistration"]["registration"])
        self.assertIsNotNone(content["data"]["verifyRegistration"]["errors"])
        self.assertEqual(
            content["data"]["verifyRegistration"]["errors"][0],
            "Email already verified.",
        )

    def test_verify_registration_verification_code_does_not_exist(self):
        self.registration.delete()

        response = self.query(
            """
            mutation VerifyRegistrationMutation($verification_code: String!) {
                verifyRegistration(verificationCode: $verification_code)
                {
                    ok,
                    registration {
                        email,
                        status,
                    },
                    errors,
                }
            }
            """,
            op_name="VerifyRegistrationMutation",
            variables={
                "verification_code": f"{self.registration.verification_code}",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["verifyRegistration"]["ok"])
        self.assertIsNone(content["data"]["verifyRegistration"]["registration"])
        self.assertIsNotNone(content["data"]["verifyRegistration"]["errors"])
        self.assertEqual(
            content["data"]["verifyRegistration"]["errors"][0],
            "Verification code does not exist.",
        )

    def test_verify_registration_verification_code_expired(self):
        forty_eight_hours_later = timezone.now() + timezone.timedelta(hours=48)

        with patch.object(timezone, "now", return_value=forty_eight_hours_later):
            response = self.query(
                """
                mutation VerifyRegistrationMutation($verification_code: String!) {
                    verifyRegistration(verificationCode: $verification_code)
                    {
                        ok,
                        registration {
                            email,
                            status,
                        },
                        errors,
                    }
                }
                """,
                op_name="VerifyRegistrationMutation",
                variables={
                    "verification_code": f"{self.registration.verification_code}",
                },
            )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["verifyRegistration"]["ok"])
        self.assertIsNone(content["data"]["verifyRegistration"]["registration"])
        self.assertIsNotNone(content["data"]["verifyRegistration"]["errors"])
        self.assertEqual(
            content["data"]["verifyRegistration"]["errors"][0],
            "Verification code expired.",
        )


@pytest.mark.django_db
@pytest.mark.enable_signals
class PasswordResetRequestTestCase(GraphQLTestCase):
    def setUp(self) -> None:
        self.user_details = dict(
            {
                "username": "test@test.com",
                "email": "test@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "test@password",
            }
        )
        User.objects.create_user(**self.user_details)

    def test_create_password_reset_request(self):
        response = self.query(
            """
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
            """,
            op_name="PasswordResetRequestMutation",
            variables={
                "email": "test@test.com",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content["data"]["createPasswordResetRequest"]["ok"])
        self.assertIsNotNone(
            content["data"]["createPasswordResetRequest"]["passwordResetRequest"]
        )
        self.assertIsNotNone(
            content["data"]["createPasswordResetRequest"]["passwordResetRequest"][
                "verificationExpiry"
            ]
        )
        self.assertEqual(mail.outbox[0].subject, "[MeerTime] Your password reset code.")

    def test_create_password_reset_request_no_email(self):
        response = self.query(
            """
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
            """,
            op_name="PasswordResetRequestMutation",
            variables={
                "email": "doesnotexist@test.com",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content["data"]["createPasswordResetRequest"]["ok"])
        self.assertIsNotNone(
            content["data"]["createPasswordResetRequest"]["passwordResetRequest"]
        )
        self.assertIsNotNone(
            content["data"]["createPasswordResetRequest"]["passwordResetRequest"][
                "verificationExpiry"
            ]
        )
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetTestCase(GraphQLTestCase):
    def setUp(self) -> None:
        self.user_details = dict(
            {
                "username": "test@test.com",
                "email": "test@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "test@password",
            }
        )
        self.user = User.objects.create_user(**self.user_details)

        # create password reset request
        self.prr = PasswordResetRequest.objects.create(
            email=self.user_details.get("email")
        )
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        self.new_password = "Abcdefgh#123"

    def test_password_reset(self):
        response = self.query(
            """
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
            """,
            op_name="PasswordResetMutation",
            variables={
                "verification_code": f"{self.prr.verification_code}",
                "password": self.new_password,
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content["data"]["passwordReset"]["ok"])
        self.assertIsNotNone(content["data"]["passwordReset"]["passwordResetRequest"])
        self.assertEqual(
            content["data"]["passwordReset"]["passwordResetRequest"]["status"],
            PasswordResetRequest.UPDATED,
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

    def test_password_reset_invalid_verification_code(self):
        response = self.query(
            """
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
            """,
            op_name="PasswordResetMutation",
            variables={
                "verification_code": "invalid_uuid_code",
                "password": self.new_password,
            },
        )

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordReset"]["ok"])
        self.assertIsNone(content["data"]["passwordReset"]["passwordResetRequest"])
        self.assertIsNotNone(content["data"]["passwordReset"]["errors"])
        self.assertEqual(
            content["data"]["passwordReset"]["errors"][0], "Invalid verification code."
        )

    def test_password_reset_verification_used(self):
        user_details = dict(
            {
                "username": "testing@test.com",
                "email": "testing@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "testing@password",
            }
        )
        User.objects.create_user(**user_details)

        # create password reset request
        prr = PasswordResetRequest.objects.create(email=user_details.get("email"))
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        new_password = "Abcdefgh#123"

        prr.status = PasswordResetRequest.UPDATED
        prr.save()

        response = self.query(
            """
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
            """,
            op_name="PasswordResetMutation",
            variables={
                "verification_code": f"{prr.verification_code}",
                "password": new_password,
            },
        )

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordReset"]["ok"])
        self.assertIsNone(content["data"]["passwordReset"]["passwordResetRequest"])
        self.assertIsNotNone(content["data"]["passwordReset"]["errors"])
        self.assertEqual(
            content["data"]["passwordReset"]["errors"][0],
            "The verification code has been used.",
        )

    def test_password_reset_verification_user_not_found(self):
        user_details = dict(
            {
                "username": "testing@test.com",
                "email": "testing@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "testing@password",
            }
        )
        user = User.objects.create_user(**user_details)

        # create password reset request
        prr = PasswordResetRequest.objects.create(email=user_details.get("email"))
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        new_password = "Abcdefgh#123"

        user.delete()

        response = self.query(
            """
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
            """,
            op_name="PasswordResetMutation",
            variables={
                "verification_code": f"{prr.verification_code}",
                "password": new_password,
            },
        )

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordReset"]["ok"])
        self.assertIsNone(content["data"]["passwordReset"]["passwordResetRequest"])
        self.assertIsNotNone(content["data"]["passwordReset"]["errors"])
        self.assertEqual(
            content["data"]["passwordReset"]["errors"][0],
            "No user found. Please contact support regarding this.",
        )

    def test_password_reset_verification_verification_code_does_not_exist(self):
        user_details = dict(
            {
                "username": "testing@test.com",
                "email": "testing@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "testing@password",
            }
        )
        User.objects.create_user(**user_details)

        # create password reset request
        prr = PasswordResetRequest.objects.create(email=user_details.get("email"))
        # clearing up the mailbox so the verification code email sent is not there anymore
        mail.outbox = []
        new_password = "Abcdefgh#123"

        prr.delete()

        response = self.query(
            """
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
            """,
            op_name="PasswordResetMutation",
            variables={
                "verification_code": f"{prr.verification_code}",
                "password": new_password,
            },
        )

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordReset"]["ok"])
        self.assertIsNone(content["data"]["passwordReset"]["passwordResetRequest"])
        self.assertIsNotNone(content["data"]["passwordReset"]["errors"])
        self.assertEqual(
            content["data"]["passwordReset"]["errors"][0],
            "Verification code does not exist.",
        )

    def test_password_reset_verification_code_expired(self):
        thirty_minutes_later = timezone.now() + timezone.timedelta(minutes=30)

        with patch.object(timezone, "now", return_value=thirty_minutes_later):
            response = self.query(
                """
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
                """,
                op_name="PasswordResetMutation",
                variables={
                    "verification_code": f"{self.prr.verification_code}",
                    "password": self.new_password,
                },
            )

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordReset"]["ok"])
        self.assertIsNone(content["data"]["passwordReset"]["passwordResetRequest"])
        self.assertIsNotNone(content["data"]["passwordReset"]["errors"])
        self.assertEqual(
            content["data"]["passwordReset"]["errors"][0],
            "The verification code has been expired.",
        )


class PasswordChangeTestCase(GraphQLTestCase):
    def setUp(self) -> None:
        self.user_details = dict(
            {
                "username": "test@test.com",
                "email": "test@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "test@password",
            }
        )
        self.user = User.objects.create_user(**self.user_details)

        self.new_password = "Abcdefgh#123"

    def test_password_change(self):
        response = self.query(
            """
            mutation PasswordChangeMutation($username: String!, $old_password: String!, $password: String!) {
                passwordChange(username: $username, oldPassword: $old_password, password: $password)
                {
                    ok,
                    user {
                        id,
                        username,
                        email,
                    },
                    errors,
                }
            }
            """,
            op_name="PasswordChangeMutation",
            variables={
                "username": self.user_details.get("username"),
                "old_password": self.user_details.get("password"),
                "password": self.new_password,
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content["data"]["passwordChange"]["ok"])
        self.assertIsNotNone(content["data"]["passwordChange"]["user"])

        self.assertIsNone(
            authenticate(
                username=self.user.username, password=self.user_details.get("password")
            )
        )
        self.assertIsNotNone(
            authenticate(username=self.user.username, password=self.new_password)
        )

    def test_password_change_same_password(self):
        response = self.query(
            """
            mutation PasswordChangeMutation($username: String!, $old_password: String!, $password: String!) {
                passwordChange(username: $username, oldPassword: $old_password, password: $password)
                {
                    ok,
                    user {
                        id,
                        username,
                        email,
                    },
                    errors,
                }
            }
            """,
            op_name="PasswordChangeMutation",
            variables={
                "username": self.user_details.get("username"),
                "old_password": self.user_details.get("password"),
                "password": self.user_details.get("password"),
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordChange"]["ok"])
        self.assertIsNone(content["data"]["passwordChange"]["user"])
        self.assertIsNotNone(content["data"]["passwordChange"]["errors"])
        self.assertEqual(
            content["data"]["passwordChange"]["errors"][0],
            "New and current passwords cannot be same.",
        )

    def test_password_change_incorrect_current_password(self):
        response = self.query(
            """
            mutation PasswordChangeMutation($username: String!, $old_password: String!, $password: String!) {
                passwordChange(username: $username, oldPassword: $old_password, password: $password)
                {
                    ok,
                    user {
                        id,
                        username,
                        email,
                    },
                    errors,
                }
            }
            """,
            op_name="PasswordChangeMutation",
            variables={
                "username": self.user_details.get("username"),
                "old_password": "incorrect_password",
                "password": self.new_password,
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordChange"]["ok"])
        self.assertIsNone(content["data"]["passwordChange"]["user"])
        self.assertIsNotNone(content["data"]["passwordChange"]["errors"])
        self.assertEqual(
            content["data"]["passwordChange"]["errors"][0],
            "Current password is incorrect.",
        )

    def test_password_change_user_does_not_exist(self):
        response = self.query(
            """
            mutation PasswordChangeMutation($username: String!, $old_password: String!, $password: String!) {
                passwordChange(username: $username, oldPassword: $old_password, password: $password)
                {
                    ok,
                    user {
                        id,
                        username,
                        email,
                    },
                    errors,
                }
            }
            """,
            op_name="PasswordChangeMutation",
            variables={
                "username": "non_existent_user",
                "old_password": "non_existent_password",
                "password": self.new_password,
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["passwordChange"]["ok"])
        self.assertIsNone(content["data"]["passwordChange"]["user"])
        self.assertIsNotNone(content["data"]["passwordChange"]["errors"])
        self.assertEqual(
            content["data"]["passwordChange"]["errors"][0], "User does not exist."
        )


@pytest.mark.django_db
@pytest.mark.enable_signals
class VerifyRegistrationTestCase(GraphQLTestCase):
    def setUp(self) -> None:
        self.user_details = dict(
            {
                "email": "test@test.com",
            }
        )
        self.provisional_user = ProvisionalUser.objects.create(**self.user_details)

    def test_activate(self):
        response = self.query(
            """
            mutation AccountActivationMutation(
                $activation_code: String!,
                $first_name: String!,
                $last_name: String!,
                $email: String!,
                $password: String!,
                $captcha: String!
            ){
                accountActivation(
                    activationCode: $activation_code,
                    userInput: {
                        firstName: $first_name,
                        lastName: $last_name,
                        email: $email,
                        password: $password,
                        captcha: $captcha
                        }
                )
                {
                    ok,
                    provisionalUser {
                        id,
                        activated,
                        activatedOn,
                    },
                    errors,
                }
            }
            """,
            op_name="AccountActivationMutation",
            variables={
                "activation_code": f"{self.provisional_user.activation_code}",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": f"{self.provisional_user.email}",
                "password": "MyPasword@123",
                "captcha": "mysecretecaptcha",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertTrue(content["data"]["accountActivation"]["ok"])
        self.assertIsNotNone(content["data"]["accountActivation"]["provisionalUser"])
        self.assertTrue(
            content["data"]["accountActivation"]["provisionalUser"]["activated"]
        )
        self.assertIsNotNone(
            content["data"]["accountActivation"]["provisionalUser"]["activatedOn"]
        )

        # check user is active
        self.provisional_user.refresh_from_db()
        self.assertTrue(self.provisional_user.user.is_active)

    def test_invalid_code(self):
        response = self.query(
            """
            mutation AccountActivationMutation(
                $activation_code: String!,
                $first_name: String!,
                $last_name: String!,
                $email: String!,
                $password: String!,
                $captcha: String!
            ){
                accountActivation(
                    activationCode: $activation_code,
                    userInput: {
                        firstName: $first_name,
                        lastName: $last_name,
                        email: $email,
                        password: $password,
                        captcha: $captcha,
                        }
                )
                {
                    ok,
                    provisionalUser {
                        id,
                        activated,
                        activatedOn,
                    },
                    errors,
                }
            }
            """,
            op_name="AccountActivationMutation",
            variables={
                "activation_code": "invalidcode",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": f"{self.provisional_user.email}",
                "password": "MyPasword@123",
                "captcha": "mysecretecaptcha",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["accountActivation"]["ok"])
        self.assertIsNone(content["data"]["accountActivation"]["provisionalUser"])
        self.assertIsNotNone(content["data"]["accountActivation"]["errors"])
        self.assertEqual(
            content["data"]["accountActivation"]["errors"][0],
            "Invalid verification code.",
        )

    def test_already_activated(self):
        self.provisional_user.activated = True
        self.provisional_user.activated_on = datetime.datetime.now()
        self.provisional_user.save()

        response = self.query(
            """
            mutation AccountActivationMutation(
                $activation_code: String!,
                $first_name: String!,
                $last_name: String!,
                $email: String!,
                $password: String!,
                $captcha: String!
            ){
                accountActivation(
                    activationCode: $activation_code,
                    userInput: {
                        firstName: $first_name,
                        lastName: $last_name,
                        email: $email,
                        password: $password,
                        captcha: $captcha
                        }
                )
                {
                    ok,
                    provisionalUser {
                        id,
                        activated,
                        activatedOn,
                    },
                    errors,
                }
            }
            """,
            op_name="AccountActivationMutation",
            variables={
                "activation_code": f"{self.provisional_user.activation_code}",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": f"{self.provisional_user.email}",
                "password": "MyPasword@123",
                "captcha": "mysecretecaptcha",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["accountActivation"]["ok"])
        self.assertIsNone(content["data"]["accountActivation"]["provisionalUser"])
        self.assertIsNotNone(content["data"]["accountActivation"]["errors"])
        self.assertEqual(
            content["data"]["accountActivation"]["errors"][0],
            "Account already activated.",
        )

    def test_activation_code_does_not_exist_for_email(self):
        response = self.query(
            """
            mutation AccountActivationMutation(
                $activation_code: String!,
                $first_name: String!,
                $last_name: String!,
                $email: String!,
                $password: String!,
                $captcha: String!
            ){
                accountActivation(
                    activationCode: $activation_code,
                    userInput: {
                        firstName: $first_name,
                        lastName: $last_name,
                        email: $email,
                        password: $password,
                        captcha: $captcha
                        }
                )
                {
                    ok,
                    provisionalUser {
                        id,
                        activated,
                        activatedOn,
                    },
                    errors,
                }
            }
            """,
            op_name="AccountActivationMutation",
            variables={
                "activation_code": f"{self.provisional_user.activation_code}",
                "first_name": "First Name",
                "last_name": "Last Name",
                "email": "different@email.com",
                "password": "MyPasword@123",
                "captcha": "mysecretecaptcha",
            },
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["accountActivation"]["ok"])
        self.assertIsNone(content["data"]["accountActivation"]["provisionalUser"])
        self.assertIsNotNone(content["data"]["accountActivation"]["errors"])
        self.assertEqual(
            content["data"]["accountActivation"]["errors"][0],
            "Activation code for this email does not exist.",
        )

    def test_activation_code_expired(self):
        thirty_days_later = timezone.now() + timezone.timedelta(days=30)

        with patch.object(timezone, "now", return_value=thirty_days_later):
            response = self.query(
                """
                mutation AccountActivationMutation(
                    $activation_code: String!,
                    $first_name: String!,
                    $last_name: String!,
                    $email: String!,
                    $password: String!,
                    $captcha: String!
                ){
                    accountActivation(
                        activationCode: $activation_code,
                        userInput: {
                            firstName: $first_name,
                            lastName: $last_name,
                            email: $email,
                            password: $password,
                            captcha: $captcha
                            }
                    )
                    {
                        ok,
                        provisionalUser {
                            id,
                            activated,
                            activatedOn,
                        },
                        errors,
                    }
                }
                """,
                op_name="AccountActivationMutation",
                variables={
                    "activation_code": f"{self.provisional_user.activation_code}",
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "email": f"{self.provisional_user.email}",
                    "password": "MyPasword@123",
                    "captcha": "mysecretecaptcha",
                },
            )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)

        self.assertFalse(content["data"]["accountActivation"]["ok"])
        self.assertIsNone(content["data"]["accountActivation"]["provisionalUser"])
        self.assertIsNotNone(content["data"]["accountActivation"]["errors"])
        self.assertEqual(
            content["data"]["accountActivation"]["errors"][0],
            "Activation code expired.",
        )
