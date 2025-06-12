from django.contrib.auth.hashers import make_password
from django.db import migrations

from meertime.settings import env
from utils.constants import UserRole

SHARED_MEERTIME_USER_ID = env("SHARED_MEERTIME_USER_ID", default="shared_id")
SHARED_MEERTIME_USER_PASS = env("SHARED_MEERTIME_USER_PASS", default="shared_pass")
SHARED_MEERTIME_USER_EMAIL = env("SHARED_MEERTIME_USER_EMAIL", default="shared_email")
SHARED_MEERTIME_USER_ACCESS = env("SHARED_MEERTIME_USER_ACCESS", default="shared_user")

SERVICE_MEERTIME_USER_ID = env("SERVICE_MEERTIME_USER_ID", default="service_id")
SERVICE_MEERTIME_USER_PASS = env("SERVICE_MEERTIME_USER_PASS", default="service_pass")
SERVICE_MEERTIME_USER_EMAIL = env("SERVICE_MEERTIME_USER_EMAIL", default="service_email")
SERVICE_MEERTIME_USER_ACCESS = env("SERVICE_MEERTIME_USER_ACCESS", default="service_user")


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
