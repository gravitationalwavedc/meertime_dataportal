import json

import responses
from django.contrib.auth import get_user_model
from django.core import mail
from graphene_django.utils.testing import GraphQLTestCase

User = get_user_model()


class ContactFormGraphQLTestCase(GraphQLTestCase):
    """Test GraphQL mutations for contact form functionality"""

    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    @responses.activate
    def test_contact_form_authenticated_contact_us(self):
        """Authenticated users can submit Contact Us form"""
        self._client.force_login(self.user)

        # Mock the captcha response
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Contact Us",
                    message: "This is a test message",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertTrue(content["data"]["submitContactForm"]["ok"])
        self.assertEqual(len(content["data"]["submitContactForm"]["errors"]), 0)

        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("Contact Us", email.subject)
        self.assertIn("Test User", email.subject)
        self.assertIn("This is a test message", email.body)
        self.assertIn("testuser@test.com", email.body)
        self.assertEqual(email.to[0], "meertime@astro.swin.edu.au")

    @responses.activate
    def test_contact_form_authenticated_report_issue_with_link(self):
        """Authenticated users can submit Report Issue with link"""
        self._client.force_login(self.user)

        # Mock the captcha response
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Report Issue",
                    message: "Data is incorrect for this pulsar",
                    link: "https://pulsars.org.au/MeerTime/J0437-4715/",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertTrue(content["data"]["submitContactForm"]["ok"])

        # Verify email contains link
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("Report Issue", email.subject)
        self.assertIn("https://pulsars.org.au/MeerTime/J0437-4715/", email.body)

    @responses.activate
    def test_contact_form_unauthenticated_with_email_name(self):
        """Unauthenticated users can submit with email and name"""
        # Mock the captcha response
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Contact Us",
                    message: "Question about data access",
                    email: "guest@example.com",
                    name: "Guest User",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertTrue(content["data"]["submitContactForm"]["ok"])

        # Verify email was sent with guest info
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("Guest User", email.subject)
        self.assertIn("guest@example.com", email.body)

    @responses.activate
    def test_contact_form_captcha_failure(self):
        """Form submission fails with invalid captcha"""
        # Mock the captcha response as failure
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": False},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Contact Us",
                    message: "Test message",
                    email: "test@example.com",
                    name: "Test",
                    captcha: "invalid_captcha"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("Captcha validation failed.", content["data"]["submitContactForm"]["errors"])

        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    @responses.activate
    def test_contact_form_report_issue_missing_link(self):
        """Report Issue requires link field"""
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Report Issue",
                    message: "There is an issue",
                    email: "test@example.com",
                    name: "Test",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("Link is required when reporting an issue.", content["data"]["submitContactForm"]["errors"])

    @responses.activate
    def test_contact_form_missing_message(self):
        """Message field is required"""
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Contact Us",
                    message: "",
                    email: "test@example.com",
                    name: "Test",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("Message is required.", content["data"]["submitContactForm"]["errors"])

    @responses.activate
    def test_contact_form_message_too_long(self):
        """Message must be at most 2000 characters"""
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        long_message = "A" * 2001

        mutation = f"""
            mutation {{
                submitContactForm(input: {{
                    contactType: "Contact Us",
                    message: "{long_message}",
                    email: "test@example.com",
                    name: "Test",
                    captcha: "test_captcha_token"
                }}) {{
                    ok
                    errors
                }}
            }}
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("2000 characters", content["data"]["submitContactForm"]["errors"][0])

    @responses.activate
    def test_contact_form_unauthenticated_missing_email(self):
        """Unauthenticated users must provide email"""
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Contact Us",
                    message: "Test message",
                    name: "Test",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("Email is required.", content["data"]["submitContactForm"]["errors"])

    @responses.activate
    def test_contact_form_unauthenticated_missing_name(self):
        """Unauthenticated users must provide name"""
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Contact Us",
                    message: "Test message",
                    email: "test@example.com",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("Name is required.", content["data"]["submitContactForm"]["errors"])

    @responses.activate
    def test_contact_form_invalid_email_format(self):
        """Email must be valid format"""
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Contact Us",
                    message: "Test message",
                    email: "invalid-email",
                    name: "Test",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("Invalid email format.", content["data"]["submitContactForm"]["errors"])

    @responses.activate
    def test_contact_form_invalid_contact_type(self):
        """Contact type must be valid"""
        responses.add(
            responses.POST,
            "https://www.google.com/recaptcha/api/siteverify",
            json={"success": True},
            status=200,
        )

        mutation = """
            mutation {
                submitContactForm(input: {
                    contactType: "Invalid Type",
                    message: "Test message",
                    email: "test@example.com",
                    name: "Test",
                    captcha: "test_captcha_token"
                }) {
                    ok
                    errors
                }
            }
        """
        response = self.query(mutation)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertFalse(content["data"]["submitContactForm"]["ok"])
        self.assertIn("Invalid contact type.", content["data"]["submitContactForm"]["errors"])
