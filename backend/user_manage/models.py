import uuid
import datetime

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.constants import UserRole


class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        max_length=150,
        blank=False,
        null=False,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    role = models.CharField(
        max_length=55,
        choices=[(r.name, r.value) for r in UserRole],
        default=UserRole.RESTRICTED.value,
    )

    def is_unrestricted(self):
        return self.role in [UserRole.UNRESTRICTED.value, UserRole.ADMIN.value]


class ProvisionalUser(models.Model):
    email = models.EmailField(
        _("email address"),
        max_length=150,
        blank=False,
        null=False,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    role = models.CharField(
        max_length=55,
        choices=[(r.name, r.value) for r in UserRole],
        default=UserRole.RESTRICTED.value,
    )

    activation_code = models.UUIDField(editable=False, default=uuid.uuid4)
    activation_expiry = models.DateTimeField(blank=True, null=True)
    activated = models.BooleanField(default=False)
    activated_on = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    email_sent_on = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.email} ({self.role})"

    def clean(self):
        if self.pk:
            # check this before activating the user
            old_instance = ProvisionalUser.objects.get(id=self.pk)
            if not old_instance.activated and self.activated and timezone.now() > self.activation_expiry:
                raise ValidationError({"activation_code": ["Activation code expired."]})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ProvisionalUser, self).save(*args, **kwargs)


class Registration(models.Model):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"

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

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        if not self.pk:
            if User.objects.filter(username=self.email).exists():
                raise ValidationError({"email": ["Email address already is in use."]})
        else:
            # we are going to update the status to 'verified'.
            old_instance = Registration.objects.get(id=self.pk)
            if old_instance.status == Registration.UNVERIFIED and self.status == Registration.VERIFIED:
                if timezone.now() > self.verification_expiry:
                    raise ValidationError({"verification_code": ["Verification code expired."]})

    def save(self, *args, **kwargs):
        self.full_clean()
        # set verification_expiry date
        if self.verification_expiry is None:
            self.verification_expiry = timezone.now() + datetime.timedelta(hours=48)

        return super(Registration, self).save(*args, **kwargs)


class PasswordResetRequest(models.Model):
    NOT_UPDATED = "NOT_UPDATED"
    UPDATED = "UPDATED"

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
