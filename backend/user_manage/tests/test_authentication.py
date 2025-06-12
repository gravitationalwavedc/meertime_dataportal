from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase

User = get_user_model()


class EmailBackendTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpassword123"
        )

    def test_authenticate_with_email(self):
        """Test that authentication works with email"""
        user = authenticate(username="test@example.com", password="testpassword123")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    def test_authenticate_with_invalid_email(self):
        """Test that authentication fails with invalid email"""
        user = authenticate(username="invalid@example.com", password="testpassword123")
        self.assertIsNone(user)

    def test_authenticate_with_wrong_password(self):
        """Test that authentication fails with wrong password"""
        user = authenticate(username="test@example.com", password="wrongpassword")
        self.assertIsNone(user)

    def test_authenticate_with_none_values(self):
        """Test that authentication fails with None values"""
        user = authenticate(username=None, password="testpassword123")
        self.assertIsNone(user)

        user = authenticate(username="test@example.com", password=None)
        self.assertIsNone(user)
