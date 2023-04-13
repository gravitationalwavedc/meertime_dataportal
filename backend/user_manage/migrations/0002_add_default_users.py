from django.db import migrations
from django.contrib.auth.hashers import make_password

from utils.constants import UserRole

import os

SHARED_MEERTIME_USER_ID = os.environ.get("SHARED_MEERTIME_USER_ID")
SHARED_MEERTIME_USER_PASS = os.environ.get("SHARED_MEERTIME_USER_PASS")
SHARED_MEERTIME_USER_EMAIL = os.environ.get("SHARED_MEERTIME_USER_EMAIL")
SHARED_MEERTIME_USER_ACCESS = os.environ.get("SHARED_MEERTIME_USER_ACCESS")

SERVICE_MEERTIME_USER_ID = os.environ.get("SERVICE_MEERTIME_USER_ID")
SERVICE_MEERTIME_USER_PASS = os.environ.get("SERVICE_MEERTIME_USER_PASS")
SERVICE_MEERTIME_USER_EMAIL = os.environ.get("SERVICE_MEERTIME_USER_EMAIL")
SERVICE_MEERTIME_USER_ACCESS = os.environ.get("SERVICE_MEERTIME_USER_ACCESS")


def add_default_users(apps, schema_editor):
    User = apps.get_model("user_manage", "User")

    # Setting the role of the user(s)
    if SHARED_MEERTIME_USER_ACCESS.strip().casefold() == UserRole.ADMIN.value.casefold():
        role = UserRole.ADMIN.value
    elif SHARED_MEERTIME_USER_ACCESS.strip().casefold() == UserRole.UNRESTRICTED.value.casefold():
        role = UserRole.UNRESTRICTED.value
    else:
        role = UserRole.RESTRICTED.value

    User.objects.create(
        username=SHARED_MEERTIME_USER_ID.strip(),
        password=make_password(SHARED_MEERTIME_USER_PASS.strip()),
        email=SHARED_MEERTIME_USER_EMAIL.strip(),
        role=role,
    )

    if SERVICE_MEERTIME_USER_ACCESS.strip().casefold() == UserRole.ADMIN.value.casefold():
        role = UserRole.ADMIN.value
    elif SERVICE_MEERTIME_USER_ACCESS.strip().casefold() == UserRole.UNRESTRICTED.value.casefold():
        role = UserRole.UNRESTRICTED.value
    else:
        role = UserRole.RESTRICTED.value

    User.objects.create(
        username=SERVICE_MEERTIME_USER_ID.strip(),
        password=make_password(SERVICE_MEERTIME_USER_PASS.strip()),
        email=SERVICE_MEERTIME_USER_EMAIL.strip(),
        role=role,
    )


def remove_default_users(apps, schema_editor):
    User = apps.get_model("user_manage", "User")

    for details in [SHARED_MEERTIME_USER_ID, SERVICE_MEERTIME_USER_ID]:
        credentials = details.split(",")
        User.objects.get(
            username=credentials[0],
        ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("user_manage", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_default_users, reverse_code=remove_default_users),
    ]
