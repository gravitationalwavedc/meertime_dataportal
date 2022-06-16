from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.utils import timezone
from uuid import UUID

from django.contrib.auth.hashers import check_password
from django.test import TestCase

from ..models import Registration, UserRole


class RegistrationTest(TestCase):

    def setUp(self):
        self.user_details = dict({
            'email': 'test@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'test@password',
        })

    def test_registration(self):
        registration = Registration.objects.create(**self.user_details)
        assert registration.status == Registration.UNVERIFIED
        assert check_password(self.user_details.get('password'), registration.password)

        try:
            UUID(str(registration.verification_code), version=4)
        except ValueError:
            assert False

        assert registration.verification_expiry > timezone.now() + timedelta(days=1, hours=23, minutes=50)
        assert registration.verification_expiry <= timezone.now() + timedelta(days=2)

    def test_registration_existing_email(self):
        user_details = dict({
            'email': 'test2@test.com',
            'first_name': 'test first name',
            'last_name': 'test last name',
            'password': 'test2@password',
        })
        Registration.objects.create(**user_details)
        with self.assertRaises(Exception) as raised:
            Registration.objects.create(**user_details)
        self.assertEqual(ValidationError, type(raised.exception))

    def test_registration_email_exists_in_user_model(self):
        modified_user_details = self.user_details.copy()
        modified_user_details.update({'username': self.user_details.get('email')})

        User.objects.create_user(**modified_user_details)
        with self.assertRaises(Exception) as raised:
            Registration.objects.create(**self.user_details)
        self.assertEqual(ValidationError, type(raised.exception))

    def test_verification_email_sent(self):
        Registration.objects.create(**self.user_details)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Please verify your email address')

    def test_verify_user_created(self):
        registration = Registration.objects.create(**self.user_details)
        registration.status = Registration.VERIFIED
        registration.save()

        try:
            user = User.objects.get(username=registration.email)
            # the user exists
            assert True

            # the user has been assigned a role (public)
            user_role = UserRole.objects.get(user=user)

            self.assertEqual(user_role.role, UserRole.RESTRICTED)

        except (User.DoesNotExist, UserRole.DoesNotExist):
            assert False
