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
        reply_to=[to],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
