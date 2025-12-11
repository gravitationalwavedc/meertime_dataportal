import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


def send_membership_rejection_email(user, project, note=None):
    """
    Send an email to notify a user that their project membership request was rejected.

    :param user: User object - the user whose request was rejected
    :param project: Project object - the project they requested to join
    :param note: str or None - optional note from the reviewer explaining the rejection
    """
    subject = f"[MeerTime Data Portal] Your request to join {project.short} ({project.code})"

    email_context = {
        "name": user.get_full_name() or user.username,
        "project_short": project.short,
        "project_code": project.code,
        "note": note,
    }

    text_message = render_to_string("dataportal/membership_rejection.txt", email_context)
    html_message = render_to_string("dataportal/membership_rejection.html", email_context)

    logger.info(f"emails.py : send_membership_rejection_email subject={subject} to={user.email}")

    try:
        send_mail(
            subject,
            text_message,
            FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        )
    except Exception as email_error:
        logger.error(f"Failed to send rejection email: {email_error}")
