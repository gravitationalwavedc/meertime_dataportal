from django.core.mail import EmailMultiAlternatives

from django.conf import settings


def get_verification_link(verification_code):
    return f'{settings.SITE_URL}verify/{verification_code}/'


def send_verification_email(
        first_name,
        last_name,
        to,
        verification_code,
        from_email=None,
):

    from_email = settings.DEFAULT_FROM_EMAIL if from_email is None else from_email
    subject = 'Please verify your email address'
    verification_link = get_verification_link(verification_code)

    text_content = f'Dear {first_name} {last_name}, You have requested an account with Meertime using this email ' \
                   f'address. Please click on the following link to verify your email address: {verification_link} . ' \
                   f'If you believe this email is sent to you by mistake please contact us at ' \
                   f'support@hpc.swin.edu.au . Kind Regards, Meertime Support Team'
    html_content = f'<p>Dear {first_name} {last_name},</p>' \
                   f'<p>You have requested an account with Meertime using this email address. Please click on the ' \
                   f'following <a href=\'{verification_link}\' target=\'_blank\'>link</a> to verify your email ' \
                   f'address:</p>' \
                   f'<p><a href=\'{verification_link}\' target=\'_blank\'>{verification_link}</a></p>' \
                   f'<p>If you believe this email is sent to you by mistake please contact us at ' \
                   f'support@hpc.swin.edu.au</p>' \
                   f'<p>Kind Regards,<br/>Meertime Support Team</p>'
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
    subject = 'Your password reset code for Meertime account.'

    text_content = f'Dear {first_name} {last_name}, You have requested to reset your password for the Meertime ' \
                   f'account. Here is the verification code for your password reset: {verification_code} . ' \
                   f'If you believe this email is sent to you by mistake please contact us at ' \
                   f'support@hpc.swin.edu.au . Kind Regards, Meertime Support Team'
    html_content = f'<p>Dear {first_name} {last_name},</p>' \
                   f'<p>You have requested to reset your password for the Meertime account. Here is the verification ' \
                   f'code for your password reset: </p>' \
                   f'<p>{verification_code}</p>' \
                   f'<p>If you believe this email is sent to you by mistake please contact us at ' \
                   f'support@hpc.swin.edu.au</p>' \
                   f'<p>Kind Regards,<br/>Meertime Support Team</p>'
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
    return f'{settings.SITE_URL}activate/{activation_code}/'


def send_activation_email(
        to,
        activation_code,
        from_email=None,
):
    from_email = settings.DEFAULT_FROM_EMAIL if from_email is None else from_email
    subject = 'Please activate your Meertime Account'
    activation_link = get_activation_link(activation_code)

    text_content = f'Dear Meertime user, We have been upgrading the user management system for the Meertime portal. ' \
                   f'As part of the upgrade, the current meertime user will be retired in 30 days. ' \
                   f'To use meertime portal after that, you would require to have your own personal account. We have ' \
                   f'created a provisional account using this email address \'{to}\'. You would need to activate ' \
                   f'your account and set a password. Please click on the following link to do that: ' \
                   f'{activation_link} . ' \
                   f'If you believe this email is sent to you by mistake please contact us at ' \
                   f'support@hpc.swin.edu.au . Kind Regards, Meertime Support Team'
    html_content = f'<p>Dear Meertime user,</p>' \
                   f'<p>We have been upgrading the user management system for the Meertime portal. As part of the ' \
                   f'upgrade, the current meertime user will be retired in 30 days. To use meertime portal after ' \
                   f'that, you would require to have your own personal account. We have created a provisional ' \
                   f'account using this email address \'{to}\'. You would need to activate your account and set a ' \
                   f'password.</p>' \
                   f'<p>Please click on the following <a href=\'{activation_link}\' target=\'_blank\'>link</a> to ' \
                   f'do that:</p>' \
                   f'<p><a href=\'{activation_link}\' target=\'_blank\'>{activation_link}</a></p>' \
                   f'<p>If you believe this email is sent to you by mistake please contact us at ' \
                   f'support@hpc.swin.edu.au</p>' \
                   f'<p>Kind Regards,<br/>Meertime Support Team</p>'
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to],
        reply_to=[from_email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
