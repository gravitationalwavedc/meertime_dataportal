import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


def send_verification_email(name, to, verification_code):
    """
    Handle sending verification email when the user registers. Triggered via a singal.

    :param str name: Full name used in the email template.
    :param str to: Email address of the recipient.
    :param str verification_code: Verification code used in the email template.
    """
    subject = "[The Pulsar Portal] Please verify your email address"
    verification_link = f"{settings.SITE_URL}/verify/{verification_code}/"
    email_context = {"name": name, "verification_link": verification_link}
    text_message = render_to_string("user_manage/verification_link.txt", email_context)
    html_message = render_to_string("user_manage/verification_link.html", email_context)

    logger.info(f"utility.py : send_verification_email subject={subject} to={to}")

    send_mail(subject, text_message, FROM_EMAIL, recipient_list=[to], html_message=html_message)


def send_password_reset_email(name, to, verification_code):
    """
    Handle sending password reset email when the user requests for a password reset. Triggered via a singal.

    :param name: str
    :param to: str
    :param verification_code: str
    """
    subject = "[The Pulsar Portal] Your password reset code."
    email_context = {"name": name, "verification_code": verification_code}
    text_message = render_to_string("user_manage/password_reset.txt", email_context)
    html_message = render_to_string("user_manage/password_reset.html", email_context)

    send_mail(subject, text_message, FROM_EMAIL, recipient_list=[to], html_message=html_message)


def send_activation_email(to, activation_code):
    """
    Handle sending the email that was needed when we upgrade the users accounts.
    Previously all users were sharing the same account, but we upgraded them to have their own account.

    It's unlikely this will be used again, but it's here just in case.

    :param to: str
    :param activation_code: str
    """
    subject = "[The Pulsar Portal] Please activate your account"
    activation_link = f"{settings.SITE_URL}activate/{activation_code}/"
    email_context = {"to": to, "activation_link": activation_link}
    text_message = render_to_string("user_manage/activation_email.txt", email_context)
    html_message = render_to_string("user_manage/activation_email.html", email_context)

    send_mail(subject, text_message, FROM_EMAIL, recipient_list=[to], html_message=html_message)
