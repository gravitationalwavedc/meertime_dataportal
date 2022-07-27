from django.db import migrations
from django.contrib.auth.hashers import make_password

from utils.constants import UserRole


def add_default_users(apps, schema_editor):
    filename = 'default_users.txt'
    print('Reading email addresses from the file')
    try:
        with open(filename, "r") as f:
            user_details = f.readlines()
    except FileNotFoundError:
        print(f'File not found with name: {filename}')
    except Exception as ex:
        print(ex)

    User = apps.get_model('user_manage', 'User')

    for details in user_details:
        credentials = details.split(',')

        # Setting the role of the user(s)
        if credentials[3].strip().casefold() == UserRole.ADMIN.value.casefold():
            role = UserRole.ADMIN.value
        elif credentials[3].strip().casefold() == UserRole.UNRESTRICTED.value.casefold():
            role = UserRole.UNRESTRICTED.value
        else:
            role = UserRole.RESTRICTED.value

        User.objects.create(
            username=credentials[0].strip(),
            password=make_password(credentials[1].strip()),
            email=credentials[2].strip(),
            role=role,
        )


def remove_default_users(apps, schema_editor):
    filename = 'default_users.txt'
    print('Reading email addresses from the file')
    try:
        with open(filename, "r") as f:
            user_details = f.readlines()
    except FileNotFoundError:
        print(f'File not found with name: {filename}')
    except Exception as ex:
        print(ex)

    User = apps.get_model('user_manage', 'User')

    for details in user_details:
        credentials = details.split(',')
        User.objects.get(
            username=credentials[0],
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('user_manage', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_users, reverse_code=remove_default_users),
    ]
