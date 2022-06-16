from django.db import migrations

from ..models import UserRole as UsrRl


def user_roles(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserRole = apps.get_model("user_manage", "UserRole")

    # for user in get_user_model().objects.all():
    for user in User.objects.all():
        role = UsrRl.RESTRICTED

        if user.is_staff:
            role = UsrRl.UNRESTRICTED

        if user.is_superuser:
            role = UsrRl.ADMIN

        UserRole.objects.create(
            user=user,
            role=role,
        )


def reverse_user_roles(apps, schema_editor):
    UserRole = apps.get_model("user_manage", "UserRole")
    UserRole.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('user_manage', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(user_roles, reverse_code=reverse_user_roles),
    ]
