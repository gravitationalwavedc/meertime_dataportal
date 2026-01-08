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

    text_message = render_to_string("dataportal/emails/projects/membership_rejection.txt", email_context)
    html_message = render_to_string("dataportal/emails/projects/membership_rejection.html", email_context)

    logger.info(f"emails.py : send_membership_rejection_email subject={subject} to={user.email}")

    send_mail(
        subject,
        text_message,
        FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )


def send_membership_request_email(managers, requester, project, message):
    """
    Send an email to notify project managers that a user has requested to join their project.

    :param managers: QuerySet of ProjectMembership objects - managers/owners to notify
    :param requester: User object - the user requesting to join
    :param project: Project object - the project they want to join
    :param message: str - the message from the requester
    """
    subject = f"[MeerTime Data Portal] New membership request for {project.short} ({project.code})"

    for membership in managers:
        manager = membership.user
        email_context = {
            "name": manager.get_full_name() or manager.username,
            "role": membership.role,
            "project_short": project.short,
            "project_code": project.code,
            "requester_name": requester.get_full_name() or requester.username,
            "requester_email": requester.email,
            "message": message or "(No message provided)",
        }

        text_message = render_to_string("dataportal/emails/projects/membership_request.txt", email_context)
        html_message = render_to_string("dataportal/emails/projects/membership_request.html", email_context)

        logger.info(f"emails.py : send_membership_request_email subject={subject} to={manager.email}")

        send_mail(
            subject,
            text_message,
            FROM_EMAIL,
            recipient_list=[manager.email],
            html_message=html_message,
        )


def send_membership_request_reminder_email(managers, requester, project, message):
    """
    Send a reminder email to project managers about a pending membership request.

    :param managers: QuerySet of ProjectMembership objects - managers/owners to notify
    :param requester: User object - the user requesting to join
    :param project: Project object - the project they want to join
    :param message: str - the message from the requester
    """
    subject = f"[MeerTime Data Portal] Reminder: Membership request for {project.short} ({project.code})"

    for membership in managers:
        manager = membership.user
        email_context = {
            "name": manager.get_full_name() or manager.username,
            "role": membership.role,
            "project_short": project.short,
            "project_code": project.code,
            "requester_name": requester.get_full_name() or requester.username,
            "requester_email": requester.email,
            "message": message or "(No message provided)",
        }

        text_message = render_to_string("dataportal/emails/projects/membership_request_reminder.txt", email_context)
        html_message = render_to_string("dataportal/emails/projects/membership_request_reminder.html", email_context)

        logger.info(f"emails.py : send_membership_request_reminder_email subject={subject} to={manager.email}")

        send_mail(
            subject,
            text_message,
            FROM_EMAIL,
            recipient_list=[manager.email],
            html_message=html_message,
        )


def send_membership_approval_email(user, project, approver_name):
    """
    Send an email to notify a user that their project membership request was approved.

    :param user: User object - the user whose request was approved
    :param project: Project object - the project they requested to join
    :param approver_name: str - name of the person who approved the request
    """
    subject = f"[MeerTime Data Portal] Your request to join {project.short} ({project.code}) was approved"

    email_context = {
        "name": user.get_full_name() or user.username,
        "project_short": project.short,
        "project_code": project.code,
        "approver_name": approver_name,
    }

    text_message = render_to_string("dataportal/emails/projects/membership_approval.txt", email_context)
    html_message = render_to_string("dataportal/emails/projects/membership_approval.html", email_context)

    logger.info(f"emails.py : send_membership_approval_email subject={subject} to={user.email}")

    send_mail(
        subject,
        text_message,
        FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )
