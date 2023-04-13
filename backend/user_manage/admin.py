from django.contrib import admin

from .models import (
    Registration,
    PasswordResetRequest,
    User,
    ProvisionalUser,
)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "password",
        "status",
        "verification_code",
        "verification_expiry",
        "created",
        "last_updated",
    ]


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "status",
        "verification_code",
        "verification_expiry",
        "created",
        "last_updated",
    ]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "password",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "role",
        "date_joined",
    ]


@admin.register(ProvisionalUser)
class ProvisionalUserAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "role",
        "activation_code",
        "activation_expiry",
        "activated",
        "activated_on",
        "created",
        "email_sent",
        "email_sent_on",
        "user",
    ]
