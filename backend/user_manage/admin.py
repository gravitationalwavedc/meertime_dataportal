from django.contrib import admin

from .models import (
    Registration,
    PasswordResetRequest,
    User,
    ProvisionalUser,
    ApiToken,
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


@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "key_preview",
        "created",
        "last_used",
        "expires_at",
        "is_active",
    ]
    list_filter = ["is_active", "created", "expires_at"]
    search_fields = ["name", "user__username", "user__email"]
    readonly_fields = ["key", "created", "last_used"]

    def key_preview(self, obj):
        """Show first 8 characters of the key for security"""
        return f"{obj.preview}..." if obj.preview else ""

    key_preview.short_description = "Token Key (preview)"
