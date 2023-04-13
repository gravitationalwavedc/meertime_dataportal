from django.core.mail import EmailMultiAlternatives

from django.conf import settings


def get_verification_link(verification_code):
    return f"{settings.SITE_URL}verify/{verification_code}/"


def send_verification_email(
    first_name,
    last_name,
    to,
    verification_code,
    from_email=None,
):

    from_email = settings.DEFAULT_FROM_EMAIL if from_email is None else from_email
    subject = "[MeerTime] Please verify your email address"
    verification_link = get_verification_link(verification_code)

    text_content = (
        f"Dear {first_name} {last_name}, You have requested an account with MeerTime using this email "
        f"address. Please click on the following link to verify your email address: {verification_link} . "
        f"If you believe this email is sent to you by mistake please contact us at "
        f"hpc-support@swin.edu.au . Kind Regards, MeerTime Support Team"
    )
    html_content = (
        f"<p>Dear {first_name} {last_name},</p>"
        f"<p>You have requested an account with MeerTime using this email address. Please click on the "
        f"following <a href='{verification_link}' target='_blank'>link</a> to verify your email "
        f"address:</p>"
        f"<p><a href='{verification_link}' target='_blank'>{verification_link}</a></p>"
        f"<p>If you believe this email is sent to you by mistake please contact us at "
        f"hpc-support@swin.edu.au</p>"
        f"<p>Kind Regards,<br/>MeerTime Support Team</p>"
    )
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to],
        reply_to=[from_email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def send_password_reset_email(
    first_name,
    last_name,
    to,
    verification_code,
    from_email=None,
):
    from_email = settings.DEFAULT_FROM_EMAIL if from_email is None else from_email
    subject = "[MeerTime] Your password reset code."

    text_content = (
        f"Dear {first_name} {last_name}, You have requested to reset your password for the MeerTime "
        f"account. Here is the verification code for your password reset: {verification_code} . "
        f"If you believe this email is sent to you by mistake please contact us at "
        f"hpc-support@swin.edu.au . Kind Regards, MeerTime Support Team"
    )
    html_content = (
        f"<p>Dear {first_name} {last_name},</p>"
        f"<p>You have requested to reset your password for the MeerTime account. Here is the verification "
        f"code for your password reset: </p>"
        f"<p>{verification_code}</p>"
        f"<p>If you believe this email is sent to you by mistake please contact us at "
        f"hpc-support@swin.edu.au</p>"
        f"<p>Kind Regards,<br/>MeerTime Support Team</p>"
    )
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to],
        reply_to=[to],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def get_activation_link(activation_code):
    return f"{settings.SITE_URL}activate/{activation_code}/"


def send_activation_email(
    to,
    activation_code,
    from_email=None,
):
    from_email = settings.DEFAULT_FROM_EMAIL if from_email is None else from_email
    subject = "[MeerTime] Please activate your account"
    activation_link = get_activation_link(activation_code)

    text_content = (
        f"Dear MeerTime user, We are upgrading the user management system for the MeerTime portal. As "
        f"part of this upgrade, the single MeerTime account (meertime) that users have been accessing the "
        f"system with will be retired on September 14, 2022. To use the MeerTime portal thereafter, "
        f"every user will require their own personal account. We have created a provisional account for "
        f"you using this email address '{to}'. You will need to activate it (with the link below) and "
        f"will be asked to set a password at that time. Please click on the following link to activate "
        f"your new account: {activation_link} . If you believe this email has been incorrectly sent to "
        f"you, please let us know at hpc-support@swin.edu.au . Kind Regards, MeerTime Support Team"
    )
    html_content = (
        f"<p>Dear MeerTime user,</p>"
        f"<p>We are upgrading the user management system for the MeerTime portal. As part of this "
        f"upgrade, the single MeerTime account (meertime) that users have been accessing the system with "
        f"will be retired on September 14, 2022. To use the MeerTime portal thereafter, every user will "
        f"require their own personal account. We have created a provisional account for you using this "
        f"email address '{to}'. You will need to activate it (with the link below) and will be asked to "
        f"set a password at that time.</p>"
        f"<p>Please click on the following <a href='{activation_link}' target='_blank'>link</a> to "
        f"activate your new account:</p>"
        f"<p><a href='{activation_link}' target='_blank'>{activation_link}</a></p>"
        f"<p>If you believe this email has been incorrectly sent to you, please let us know at "
        f"hpc-support@swin.edu.au</p>"
        f"<p>Kind Regards,<br/>MeerTime Support Team</p>"
    )
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to],
        reply_to=[from_email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
