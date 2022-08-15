from django.db import migrations
from django.contrib.auth.hashers import make_password

from utils.constants import UserRole

import os

API_ADMIN_USER_ID = os.environ.get('API_ADMIN_USER_ID')
API_ADMIN_USER_PASS = os.environ.get('API_ADMIN_USER_PASS')
API_ADMIN_USER_EMAIL = os.environ.get('API_ADMIN_USER_EMAIL')


def add_default_users(apps, schema_editor):
    User = apps.get_model('user_manage', 'User')

    # Setting the role of the user(s)
    role = UserRole.ADMIN.value

    User.objects.create(
        username=API_ADMIN_USER_ID.strip(),
        password=make_password(API_ADMIN_USER_PASS.strip()),
        email=API_ADMIN_USER_EMAIL.strip(),
        role=role,
    )


def remove_default_users(apps, schema_editor):
    User = apps.get_model('user_manage', 'User')

    for username in [API_ADMIN_USER_ID]:
        User.objects.get(
            username=username,
        ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('user_manage', '0003_add_meertime_svc_permission'),
    ]

    operations = [
        migrations.RunPython(add_default_users, reverse_code=remove_default_users),
    ]
