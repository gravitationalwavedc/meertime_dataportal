from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from uuid import UUID

from django.contrib.auth.hashers import check_password
from django.test import TestCase

from utils.constants import UserRole
from ..models import Registration, ProvisionalUser

User = get_user_model()


class RegistrationTest(TestCase):
    def setUp(self):
        self.user_details = dict(
            {
                "email": "test@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "test@password",
            }
        )

    def test_registration(self):
        registration = Registration.objects.create(**self.user_details)
        self.assertEqual(registration.status, Registration.UNVERIFIED)
        self.assertTrue(check_password(self.user_details.get("password"), registration.password))

        try:
            UUID(str(registration.verification_code), version=4)
        except ValueError:
            self.fail("Invalid UUID format")

        self.assertGreater(registration.verification_expiry, timezone.now() + timedelta(days=1, hours=23, minutes=50))
        self.assertLessEqual(registration.verification_expiry, timezone.now() + timedelta(days=2))

    def test_registration_existing_email(self):
        user_details = dict(
            {
                "email": "test2@test.com",
                "first_name": "test first name",
                "last_name": "test last name",
                "password": "test2@password",
            }
        )
        Registration.objects.create(**user_details)
        with self.assertRaises(Exception) as raised:
            Registration.objects.create(**user_details)
        self.assertEqual(ValidationError, type(raised.exception))

    def test_registration_email_exists_in_user_model(self):
        modified_user_details = self.user_details.copy()
        modified_user_details.update({"username": self.user_details.get("email")})

        User.objects.create_user(**modified_user_details)
        with self.assertRaises(Exception) as raised:
            Registration.objects.create(**self.user_details)
        self.assertEqual(ValidationError, type(raised.exception))

    def test_verification_email_sent(self):
        Registration.objects.create(**self.user_details)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[MeerTime] Please verify your email address")

    def test_verify_user_created(self):
        registration = Registration.objects.create(**self.user_details)
        registration.status = Registration.VERIFIED
        registration.save()

        try:
            user = User.objects.get(username=registration.email)
            # the user exists
            self.assertTrue(True)

            # the user has been assigned a role (public)
            self.assertEqual(user.role, UserRole.RESTRICTED.value)

        except User.DoesNotExist:
            self.fail("User does not exist")


class ProvisionalUserTest(TestCase):
    def setUp(self):
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

    def test_provisional_user(self):
        provisional_user = ProvisionalUser.objects.create(
            email="prvusr@test.com",
            role=UserRole.UNRESTRICTED.value,
        )
        self.assertEqual(provisional_user.role, UserRole.UNRESTRICTED.value)

        try:
            UUID(str(provisional_user.activation_code), version=4)
        except ValueError:
            self.fail("Invalid UUID format")

        self.assertGreater(
            provisional_user.activation_expiry, timezone.now() + timedelta(days=29, hours=23, minutes=50)
        )
        self.assertLessEqual(provisional_user.activation_expiry, timezone.now() + timedelta(days=30))

        self.assertTrue(provisional_user.email_sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[MeerTime] Please activate your account")

        self.assertEqual(provisional_user.user.role, UserRole.UNRESTRICTED.value)
        self.assertFalse(provisional_user.user.is_active)

    def test_existing_user(self):
        with self.assertRaises(Exception) as raised:
            ProvisionalUser.objects.create(
                email="test@test.com",
                role=UserRole.UNRESTRICTED.value,
            )
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_existing_provisional_user(self):
        ProvisionalUser.objects.create(
            email="existing@test.com",
            role=UserRole.UNRESTRICTED.value,
        )
        with self.assertRaises(Exception) as raised:
            ProvisionalUser.objects.create(
                email="existing@test.com",
                role=UserRole.UNRESTRICTED.value,
            )
        self.assertEqual(ValidationError, type(raised.exception))
