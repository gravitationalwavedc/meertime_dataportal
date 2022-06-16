import uuid
import datetime

from django.utils import timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


User = get_user_model()


class Registration(models.Model):
    UNVERIFIED = 'UNVERIFIED'
    VERIFIED = 'VERIFIED'

    STATUS = [
        (UNVERIFIED, UNVERIFIED),
        (VERIFIED, VERIFIED),
    ]

    first_name = models.CharField(max_length=255, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(blank=False, null=False, unique=True)
    password = models.CharField(max_length=255, blank=False, null=False)
    status = models.CharField(max_length=55, choices=STATUS, default=UNVERIFIED)
    verification_code = models.UUIDField(editable=False, default=uuid.uuid4)
    verification_expiry = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.CASCADE)

    def clean(self):
        if not self.pk:
            if User.objects.filter(username=self.email).exists():
                raise ValidationError({'email': ['Email address already is in use.']})
        else:
            # we are going to update the satus to 'verified'.
            old_instance = Registration.objects.get(id=self.pk)
            if old_instance.status == Registration.UNVERIFIED and self.status == Registration.VERIFIED:
                if timezone.now() > self.verification_expiry:
                    raise ValidationError({'verification_code': ['Verification code expired.']})

    def save(self, *args, **kwargs):
        self.full_clean()
        # set verification_expiry date
        if self.verification_expiry is None:
            self.verification_expiry = timezone.now() + datetime.timedelta(hours=48)

        return super(Registration, self).save(*args, **kwargs)


class PasswordResetRequest(models.Model):
    NOT_UPDATED = 'NOT_UPDATED'
    UPDATED = 'UPDATED'

    STATUS = [
        (NOT_UPDATED, NOT_UPDATED),
        (UPDATED, UPDATED),
    ]

    email = models.EmailField(blank=False, null=False)
    status = models.CharField(max_length=55, choices=STATUS, default=NOT_UPDATED)
    verification_code = models.UUIDField(editable=False, default=uuid.uuid4)
    verification_expiry = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        # set verification_expiry date
        if self.verification_expiry is None:
            self.verification_expiry = timezone.now() + datetime.timedelta(minutes=30)

        return super(PasswordResetRequest, self).save(*args, **kwargs)


class UserRole(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False)

    RESTRICTED = 'RESTRICTED'  # restricted role can have no access to the embargoed data
    UNRESTRICTED = 'UNRESTRICTED'  # unrestricted should be able to view any data
    ADMIN = 'ADMIN'  # admin to get additional access, ex: change restricted to unrestricted

    ROLE_CHOICES = [
        (ADMIN, ADMIN),
        (RESTRICTED, RESTRICTED),
        (UNRESTRICTED, UNRESTRICTED),
    ]

    role = models.CharField(max_length=55, choices=ROLE_CHOICES, default=RESTRICTED)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
