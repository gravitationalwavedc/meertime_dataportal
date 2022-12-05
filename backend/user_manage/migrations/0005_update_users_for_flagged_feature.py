from django.db import migrations


TO_UPDATE = [
    'ssaleheen@swin.edu.au',
    'mbailes@swin.edu.au',
    'andrewcameron@swin.edu.au',
    'jaleslie@swin.edu.au',
]


def update_users(apps, schema_editor):
    User = apps.get_model('user_manage', 'User')

    # Setting the staff status to the users
    for username in TO_UPDATE:
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.save()
        except User.DoesNotExist:
            pass


def reset_users(apps, schema_editor):
    User = apps.get_model('user_manage', 'User')

    # update the staff status to the users
    for username in TO_UPDATE:
        try:
            user = User.objects.get(username=username)
            user.is_staff = False
            user.save()
        except User.DoesNotExist:
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('user_manage', '0004_add_api_admin_user'),
    ]

    operations = [
        migrations.RunPython(update_users, reverse_code=reset_users),
    ]
