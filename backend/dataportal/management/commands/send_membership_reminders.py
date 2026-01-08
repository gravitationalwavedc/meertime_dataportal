import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from dataportal.emails import send_membership_request_reminder_email
from dataportal.models import ProjectMembershipRequest

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send reminder emails to project managers about pending membership requests"

    def handle(self, *args, **options):
        """
        Send reminder emails for pending membership requests:
        - First reminder: 7 days after initial request (last_reminder_sent_at is NULL)
        - Subsequent reminders: 7 days after last reminder was sent
        """
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)

        # Find requests needing first reminder (7+ days old, no reminder sent yet)
        first_reminders = ProjectMembershipRequest.objects.filter(
            status=ProjectMembershipRequest.StatusChoices.PENDING,
            requested_at__lte=seven_days_ago,
            last_reminder_sent_at__isnull=True,
        )

        # Find requests needing subsequent reminders (last reminder 7+ days ago)
        subsequent_reminders = ProjectMembershipRequest.objects.filter(
            status=ProjectMembershipRequest.StatusChoices.PENDING,
            last_reminder_sent_at__lte=seven_days_ago,
        )

        # Combine both querysets
        requests_to_remind = first_reminders | subsequent_reminders

        if not requests_to_remind.exists():
            self.stdout.write(self.style.SUCCESS("No pending membership requests require reminders."))
            logger.info("send_membership_reminders: No requests require reminders")
            return

        reminder_count = 0
        for request in requests_to_remind:
            # Get all managers and owners for this project
            managers = request.project.get_managers_and_owners()

            if not managers.exists():
                logger.warning(
                    f"send_membership_reminders: No active managers found for project {request.project.code}"
                )
                continue

            # Send reminder email to all managers
            send_membership_request_reminder_email(
                managers=managers,
                requester=request.user,
                project=request.project,
                message=request.message,
            )

            # Update last_reminder_sent_at timestamp
            request.last_reminder_sent_at = now
            request.save(update_fields=["last_reminder_sent_at"])

            reminder_count += 1
            logger.info(
                f"send_membership_reminders: Sent reminder for request {request.id} "
                f"(user: {request.user.username}, project: {request.project.code})"
            )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully sent {reminder_count} reminder email(s) to project managers.")
        )
        logger.info(f"send_membership_reminders: Completed. Sent {reminder_count} reminders")
