from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from utils.constants import UserRole

from ..models import ApiToken, ProvisionalUser, Registration

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
        self.assertEqual(mail.outbox[0].subject, "[The Pulsar Portal] Please verify your email address")

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
        self.assertEqual(mail.outbox[0].subject, "[The Pulsar Portal] Please activate your account")

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


class ApiTokenModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
            role=UserRole.UNRESTRICTED.value,
        )

    def test_token_auto_generates_key_on_save(self):
        """Test that tokens automatically generate a key when saved"""
        token = ApiToken(user=self.user, name="Test Token")
        token.save()
        self.assertIsNotNone(token.key)
        self.assertTrue(len(token.key) > 20)  # Should be a reasonable length

    def test_token_default_expiry_on_creation(self):
        """Test that new tokens get a default expiry based on configured days"""
        token = ApiToken.objects.create(user=self.user, name="Test Token")

        # Check that expires_at is set to approximately the configured days from now
        expected_expiry = timezone.now() + timedelta(days=settings.API_TOKEN_DEFAULT_EXPIRY_DAYS)
        self.assertIsNotNone(token.expires_at)

        # Allow for a small time difference (within 1 minute) for test execution time
        time_diff = abs((token.expires_at - expected_expiry).total_seconds())
        self.assertLess(
            time_diff,
            60,
            f"Expiry should be within 1 minute of expected {settings.API_TOKEN_DEFAULT_EXPIRY_DAYS}-day expiry",
        )

    def test_token_explicit_expires_at_none_preserved(self):
        """Test that explicitly setting expires_at=None is preserved (never expires)"""
        # Note: This tests the save() method behavior for admin-created tokens
        token = ApiToken.objects.create(user=self.user, name="Never Expires Token")
        token.expires_at = None
        token.save()

        # Refresh from database
        token.refresh_from_db()
        self.assertIsNone(token.expires_at)
        self.assertFalse(token.is_expired())

    def test_token_explicit_expiry_date_preserved(self):
        """Test that explicitly setting a custom expiry date is preserved"""
        custom_expiry = timezone.now() + timedelta(days=30)
        token = ApiToken.objects.create(user=self.user, name="Custom Expiry Token", expires_at=custom_expiry)

        # Refresh from database
        token.refresh_from_db()
        self.assertEqual(token.expires_at, custom_expiry)

    def test_token_is_expired_method(self):
        """Test the is_expired() method"""
        # Test token that expires in the future
        future_token = ApiToken.objects.create(
            user=self.user, name="Future Token", expires_at=timezone.now() + timedelta(days=1)
        )
        self.assertFalse(future_token.is_expired())

        # Test token that expired in the past
        past_token = ApiToken.objects.create(
            user=self.user, name="Past Token", expires_at=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(past_token.is_expired())

        # Test token that never expires
        never_expires_token = ApiToken.objects.create(user=self.user, name="Never Expires", expires_at=None)
        self.assertFalse(never_expires_token.is_expired())

    def test_token_str_representation(self):
        """Test the string representation of ApiToken"""
        token = ApiToken.objects.create(user=self.user, name="Test Token")
        expected_str = f"{self.user.username} - Test Token"
        self.assertEqual(str(token), expected_str)

    def test_multiple_tokens_per_user(self):
        """Test that users can have multiple tokens"""
        token1 = ApiToken.objects.create(user=self.user, name="Token 1")
        token2 = ApiToken.objects.create(user=self.user, name="Token 2")

        user_tokens = ApiToken.objects.filter(user=self.user)
        self.assertEqual(user_tokens.count(), 2)
        self.assertIn(token1, user_tokens)
        self.assertIn(token2, user_tokens)

    def test_token_name_unique_per_user(self):
        """Test that token names must be unique per user"""
        # Create first token
        ApiToken.objects.create(user=self.user, name="My Token")

        # Attempting to create another token with the same name for the same user should fail
        with self.assertRaises(IntegrityError):
            ApiToken.objects.create(user=self.user, name="My Token")

    def test_token_name_can_be_same_for_different_users(self):
        """Test that different users can have tokens with the same name"""
        # Create another user
        other_user = User.objects.create_user(
            username="otheruser@example.com",
            email="otheruser@example.com",
            password="testpass123",
            role=UserRole.UNRESTRICTED.value,
        )

        # Both users can have tokens with the same name
        token1 = ApiToken.objects.create(user=self.user, name="My Token")
        token2 = ApiToken.objects.create(user=other_user, name="My Token")

        self.assertEqual(token1.name, token2.name)
        self.assertNotEqual(token1.user, token2.user)
