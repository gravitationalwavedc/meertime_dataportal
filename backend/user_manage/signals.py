import datetime
import logging

from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import PasswordResetRequest, ProvisionalUser, Registration, User
from .utility import send_activation_email, send_password_reset_email, send_verification_email

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Registration, dispatch_uid="send_out_email")
def send_out_email(sender, instance, **kwargs):
    """
    After a Registration object is saved an email is sent to the user to verify their account
    using a verification code.

    :param sender: Registration model class.
    :param instance: Instance of a registration model that called save.
    :param kwargs: Extra keyword arguments.
    """
    if instance.status is not Registration.VERIFIED:
        # send verification email
        send_verification_email(
            name=instance.get_full_name(),
            to=instance.email,
            verification_code=instance.verification_code,
        )


@receiver(pre_save, sender=Registration, dispatch_uid="handle_registration_save")
def handle_registration_save(sender, instance, **kwargs):
    """
    Before a Registration object is saved, we hash the password and create a new user if the
    registration is verified and no user is associated with it.
    Email is used as the username and we create a hashed password if needed.

    :param sender: Registration model class.
    :param instance: Instance of a registration model that called save.
    :param kwargs: Extra keyword arguments.
    """
    if not instance.pk:
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
    """
    Before a PasswordResetRequest object is saved, we send an email to the user to reset their
    password using a verification code.

    :param sender: PasswordResetRequest model class.
    :param instance: Instance of a password reset request model that called save.
    :param raw: True if the model is saved exactly as presented.
    :param kwargs: Extra keyword arguments.
    """
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
    """
    Before a ProvisionalUser object is saved, we create a new user if there is no instance pk
    (This usually means it hasn't been saved before). Then we check if an email has been sent, if not
    we send an activation email and update the model so it's not sent again.

    :param sender: ProvisionalUser model class.
    :param instance: Instance of a provisional user model that called save.
    :param kwargs: Extra keyword arguments.
    """
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
        instance.activation_expiry = now + datetime.timedelta(days=30)

        send_activation_email(
            to=instance.email,
            activation_code=instance.activation_code,
        )

        instance.email_sent = True
        instance.email_sent_on = now
