from django.contrib.auth.hashers import make_password
from django.db import migrations

from meertime.settings import env
from utils.constants import UserRole

API_ADMIN_USER_ID = env("API_ADMIN_USER_ID", default="user_api_admin")
API_ADMIN_USER_PASS = env("API_ADMIN_USER_PASS", default="password_api_admin")
API_ADMIN_USER_EMAIL = env("API_ADMIN_USER_EMAIL", default="example@superuser.com")


def add_default_users(apps, schema_editor):
    User = apps.get_model("user_manage", "User")

    # Setting the role of the user(s)
    role = UserRole.ADMIN.value

    User.objects.create(
        username=API_ADMIN_USER_ID.strip(),
        password=make_password(API_ADMIN_USER_PASS.strip()),
        email=API_ADMIN_USER_EMAIL.strip(),
        role=role,
    )


def remove_default_users(apps, schema_editor):
    User = apps.get_model("user_manage", "User")

    for username in [API_ADMIN_USER_ID]:
        User.objects.get(
            username=username,
        ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user_manage", "0003_add_meertime_svc_permission"),
    ]

    operations = [
        migrations.RunPython(add_default_users, reverse_code=remove_default_users),
    ]
