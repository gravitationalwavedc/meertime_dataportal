from django.contrib import admin

from .models import (
    Registration,
    PasswordResetRequest, UserRole,
)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'email',
        'password',
        'status',
        'verification_code',
        'verification_expiry',
        'created',
        'last_updated',
    ]


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'status',
        'verification_code',
        'verification_expiry',
        'created',
        'last_updated',
    ]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'role',
        'created',
        'last_updated',
    ]
