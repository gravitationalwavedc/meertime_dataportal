from datetime import timedelta
from io import StringIO
import logging

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from dataportal.models import (
    MainProject,
    Project,
    ProjectMembership,
    ProjectMembershipRequest,
    Telescope,
)

User = get_user_model()


@override_settings(
    LOGGING={
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "null": {
                "class": "logging.NullHandler",
            },
        },
        "loggers": {
            "dataportal.management.commands.send_membership_reminders": {
                "handlers": ["null"],
                "level": "CRITICAL",
                "propagate": False,
            },
        },
    }
)
class SendMembershipRemindersCommandTestCase(TestCase):
    """Test the send_membership_reminders management command"""

    def setUp(self):
        """Set up test data"""
        # Suppress logging during tests
        logging.getLogger("dataportal.management.commands.send_membership_reminders").setLevel(logging.CRITICAL)

        # Create telescope and main project
        self.telescope = Telescope.objects.create(name="MeerKAT")
        self.main_project = MainProject.objects.create(
            name="MeerTime",
            telescope=self.telescope,
        )

        # Create project
        self.project = Project.objects.create(
            main_project=self.main_project,
            code="TPA",
            short="TPA",
            description="Thousand Pulsar Array",
        )

        # Create users
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="testpass123",
            first_name="Owner",
            last_name="User",
        )
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="testpass123",
            first_name="Manager",
            last_name="User",
        )
        self.requester = User.objects.create_user(
            username="requester",
            email="requester@test.com",
            password="testpass123",
        )

        # Create memberships
        ProjectMembership.objects.create(
            user=self.owner,
            project=self.project,
            role=ProjectMembership.RoleChoices.OWNER,
        )
        ProjectMembership.objects.create(
            user=self.manager,
            project=self.project,
            role=ProjectMembership.RoleChoices.MANAGER,
        )

    def test_first_reminder_sent_after_7_days(self):
        """First reminder is sent 7+ days after initial request"""
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7, hours=1)

        # Create request 7 days + 1 hour ago
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request.requested_at = seven_days_ago
        request.save(update_fields=["requested_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify emails were sent to both owner and manager
        self.assertEqual(len(mail.outbox), 2)
        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn(self.owner.email, recipients)
        self.assertIn(self.manager.email, recipients)

        # Verify last_reminder_sent_at was updated
        request.refresh_from_db()
        self.assertIsNotNone(request.last_reminder_sent_at)
        self.assertAlmostEqual(
            request.last_reminder_sent_at.timestamp(),
            now.timestamp(),
            delta=5,  # Within 5 seconds
        )

    def test_first_reminder_not_sent_before_7_days(self):
        """First reminder is NOT sent before 7 days"""
        now = timezone.now()
        six_days_23_hours_ago = now - timedelta(days=6, hours=23)

        # Create request 6 days + 23 hours ago (just under 7 days)
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request.requested_at = six_days_23_hours_ago
        request.save(update_fields=["requested_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify no emails were sent
        self.assertEqual(len(mail.outbox), 0)

        # Verify last_reminder_sent_at was NOT updated
        request.refresh_from_db()
        self.assertIsNone(request.last_reminder_sent_at)

    def test_subsequent_reminder_sent_after_7_days(self):
        """Subsequent reminder is sent 7+ days after last reminder"""
        now = timezone.now()
        fourteen_days_ago = now - timedelta(days=14)
        seven_days_ago = now - timedelta(days=7, hours=1)

        # Create request with last reminder sent 7+ days ago
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request.requested_at = fourteen_days_ago
        request.last_reminder_sent_at = seven_days_ago
        request.save(update_fields=["requested_at", "last_reminder_sent_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify emails were sent to both owner and manager
        self.assertEqual(len(mail.outbox), 2)

        # Verify last_reminder_sent_at was updated
        request.refresh_from_db()
        self.assertAlmostEqual(
            request.last_reminder_sent_at.timestamp(),
            now.timestamp(),
            delta=5,  # Within 5 seconds
        )

    def test_subsequent_reminder_not_sent_before_7_days(self):
        """Subsequent reminder is NOT sent before 7 days since last reminder"""
        now = timezone.now()
        fourteen_days_ago = now - timedelta(days=14)
        six_days_ago = now - timedelta(days=6, hours=23)

        # Create request with last reminder sent just under 7 days ago
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request.requested_at = fourteen_days_ago
        request.last_reminder_sent_at = six_days_ago
        request.save(update_fields=["requested_at", "last_reminder_sent_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify no emails were sent
        self.assertEqual(len(mail.outbox), 0)

    def test_approved_requests_excluded(self):
        """Approved requests do not receive reminders"""
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7, hours=1)

        # Create approved request
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.APPROVED,
        )
        request.requested_at = seven_days_ago
        request.save(update_fields=["requested_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify no emails were sent
        self.assertEqual(len(mail.outbox), 0)

    def test_rejected_requests_excluded(self):
        """Rejected requests do not receive reminders"""
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7, hours=1)

        # Create rejected request
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.REJECTED,
        )
        request.requested_at = seven_days_ago
        request.save(update_fields=["requested_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify no emails were sent
        self.assertEqual(len(mail.outbox), 0)

    def test_managers_receive_emails(self):
        """All managers and owners receive reminder emails"""
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7, hours=1)

        # Create request
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request.requested_at = seven_days_ago
        request.save(update_fields=["requested_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify emails were sent to both owner and manager
        self.assertEqual(len(mail.outbox), 2)
        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn(self.owner.email, recipients)
        self.assertIn(self.manager.email, recipients)

        # Verify email content
        for email in mail.outbox:
            self.assertIn("Reminder", email.subject)
            self.assertIn("TPA", email.subject)
            self.assertIn("Please let me join", email.body)

    def test_multiple_projects_processed(self):
        """Multiple pending requests across different projects are all processed"""
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7, hours=1)

        # Create second project
        project2 = Project.objects.create(
            main_project=self.main_project,
            code="RELBIN",
            short="RELBIN",
            description="Relativistic Binaries",
        )
        ProjectMembership.objects.create(
            user=self.owner,
            project=project2,
            role=ProjectMembership.RoleChoices.OWNER,
        )

        # Create requests for both projects
        request1 = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Request 1",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request1.requested_at = seven_days_ago
        request1.save(update_fields=["requested_at"])

        request2 = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=project2,
            message="Request 2",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request2.requested_at = seven_days_ago
        request2.save(update_fields=["requested_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # Verify emails were sent (2 managers for project1, 1 owner for project2 = 3 total)
        self.assertEqual(len(mail.outbox), 3)

        # Verify both requests were updated
        request1.refresh_from_db()
        request2.refresh_from_db()
        self.assertIsNotNone(request1.last_reminder_sent_at)
        self.assertIsNotNone(request2.last_reminder_sent_at)

    def test_no_reminders_needed(self):
        """Command handles case when no reminders are needed"""
        # Don't create any requests

        # Run command
        out = StringIO()
        call_command("send_membership_reminders", stdout=out, verbosity=0)

        # Verify no emails were sent
        self.assertEqual(len(mail.outbox), 0)

        # Verify output message
        self.assertIn("No pending membership requests require reminders", out.getvalue())

    def test_timing_precision_at_exactly_7_days(self):
        """Test timing precision at exactly 7 days boundary"""
        now = timezone.now()
        exactly_seven_days_ago = now - timedelta(days=7)

        # Create request at exactly 7 days ago
        request = ProjectMembershipRequest.objects.create(
            user=self.requester,
            project=self.project,
            message="Please let me join",
            status=ProjectMembershipRequest.StatusChoices.PENDING,
        )
        request.requested_at = exactly_seven_days_ago
        request.save(update_fields=["requested_at"])

        # Run command
        call_command("send_membership_reminders", stdout=StringIO(), verbosity=0)

        # At exactly 7 days, the reminder should be sent (using <=)
        self.assertEqual(len(mail.outbox), 2)

        # Verify last_reminder_sent_at was updated
        request.refresh_from_db()
        self.assertIsNotNone(request.last_reminder_sent_at)
