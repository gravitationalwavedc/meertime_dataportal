from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Registration, PasswordResetRequest
from .utility import send_verification_email
from .utility import send_password_reset_email


@receiver(pre_save, sender=Registration, dispatch_uid='handle_registration_save')
def handle_registration_save(sender, instance, **kwargs):
    if not instance.pk:
        # hashing the password
        instance.password = make_password(instance.password)

        # send verification email
        send_verification_email(
            first_name=instance.first_name,
            last_name=instance.last_name,
            to=instance.email,
            verification_code=instance.verification_code,
        )
    else:
        if instance.status == Registration.VERIFIED and instance.user is None:
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


@receiver(pre_save, sender=PasswordResetRequest, dispatch_uid='handle_request_password_reset_save')
def handle_password_reset_request_save(sender, instance, raw, **kwargs):
    if not instance.pk and not raw:
        # get the user whose password will be changed
        user = User.objects.filter(Q(username=instance.email) | Q(email=instance.email)).first()
        # No user means it should fail silently
        if not user:
            return

        # send verification email
        send_password_reset_email(
            first_name=user.first_name,
            last_name=user.last_name,
            to=user.email,
            verification_code=instance.verification_code,
        )
