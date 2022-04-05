import uuid
import datetime

from django.utils import timezone

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


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
            self.verification_expiry = timezone.now() + datetime.timedelta(days=2)

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
