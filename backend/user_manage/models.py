import datetime
import secrets
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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


class ApiToken(models.Model):
    """
    Bearer token model for API authentication
    Similar to Django REST Framework's Token model but with additional features
    """

    key = models.CharField(max_length=settings.API_TOKEN_MAX_LENGTH, unique=True, db_index=True)
    user = models.ForeignKey(User, related_name="api_tokens", on_delete=models.CASCADE, verbose_name=_("User"))
    name = models.CharField(max_length=64, default="API Token")
    created = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("API Token")
        verbose_name_plural = _("API Tokens")
        constraints = [models.UniqueConstraint(fields=["user", "name"], name="unique_token_name_per_user")]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def preview(self):
        """Return first 8 characters of the token key for display purposes"""
        return self.key[:8] if self.key else ""

    def is_expired(self):
        """Check if token is expired"""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if token is valid (active and not expired)"""
        return self.is_active and not self.is_expired()

    def update_last_used(self):
        """Update the last_used timestamp"""
        self.last_used = timezone.now()
        self.save(update_fields=["last_used"])

    def save(self, *args, **kwargs):
        if not self.key:
            token_bytes = settings.API_TOKEN_BYTES
            self.key = secrets.token_urlsafe(token_bytes)

        # Set default expiry for new tokens based on configured days
        # Only if expires_at is None and it wasn't explicitly set to None
        if not self.pk and self.expires_at is None:
            expiry_days = settings.API_TOKEN_DEFAULT_EXPIRY_DAYS
            self.expires_at = timezone.now() + datetime.timedelta(days=expiry_days)

        super().save(*args, **kwargs)


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
