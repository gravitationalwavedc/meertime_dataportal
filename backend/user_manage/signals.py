import datetime
import logging

from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Registration, PasswordResetRequest, User, ProvisionalUser
from .utility import (
    send_verification_email,
    send_password_reset_email,
    send_activation_email,
)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Registration, dispatch_uid="send_out_email")
def send_out_email(sender, instance, **kwargs):
    if instance.status is not Registration.VERIFIED:
        # send verification email
        send_verification_email(
            name=instance.get_full_name(),
            to=instance.email,
            verification_code=instance.verification_code,
        )


@receiver(pre_save, sender=Registration, dispatch_uid="handle_registration_save")
def handle_registration_save(sender, instance, **kwargs):
    if not instance.pk:
        # hashing the password
        instance.password = make_password(instance.password)

        logger.info(
            f"""signals.py: handle_registration_save
                fn={instance.first_name}
                ln={instance.last_name}
                email={instance.email}
                status={instance.status}
                vcode={instance.verification_code}
                user={instance.user}
                time={datetime.datetime}"""
        )

    elif instance.status == Registration.VERIFIED and instance.user is None:
        # if verified, and no user is associated with then, create a new user, with
        # the username as the email
        # a password that is hash of the hashed password
        new_user = User.objects.create_user(
            username=instance.email,
            email=instance.email,
            password=instance.password,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )

        # forcefully update the password of the user to make sure the hash is correct
        new_user.password = instance.password
        new_user.save()

        instance.user = new_user


@receiver(pre_save, sender=PasswordResetRequest, dispatch_uid="handle_request_password_reset_save")
def handle_password_reset_request_save(sender, instance, raw, **kwargs):
    if not instance.pk and not raw:
        # get the user whose password will be changed
        user = User.objects.filter(Q(username=instance.email) | Q(email=instance.email)).first()
        # No user means it should fail silently
        if not user:
            return

        # send verification email
        send_password_reset_email(
            name=user.get_full_name(),
            to=user.email,
            verification_code=instance.verification_code,
        )


@receiver(pre_save, sender=ProvisionalUser, dispatch_uid="handle_provisional_user_save")
def handle_provisional_user_save(sender, instance, **kwargs):
    if not instance.pk:
        # create a new user and refer it
        new_user = User.objects.create_user(
            username=instance.email,
            email=instance.email,
            is_active=False,
            role=instance.role,
        )
        instance.user = new_user

    # send activation email whenever we see that email hasn't been sent
    # this can be used to resend emails
    if not instance.email_sent:
        now = timezone.now()
        # update expiry
        instance.activation_expiry = now + datetime.timedelta(days=30)

        try:
            send_activation_email(
                to=instance.email,
                activation_code=instance.activation_code,
            )
        except Exception as ex:
            print("Email was not sent due to an error")
            print(ex)
        else:
            instance.email_sent = True
            instance.email_sent_on = now
