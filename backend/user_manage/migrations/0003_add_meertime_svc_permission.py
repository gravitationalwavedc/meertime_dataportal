from django.db import migrations


def add_permission(apps, schema_editor):
    User = apps.get_model('user_manage', 'User')
    Permission = apps.get_model('auth', 'Permission')

    svc_user = User.objects.get(username='meertime-svc')

    permissions = Permission.objects.filter(content_type__app_label='dataportal', codename__iregex=r'^add_')
    for p in permissions:
        svc_user.user_permissions.add(p)
        print(f'User {svc_user.username} has been granted the permission Permission {p.codename}')


def remove_permission(apps, schema_editor):
    User = apps.get_model('user_manage', 'User')

    svc_user = User.objects.get(username='meertime-svc')

    svc_user.user_permissions.filter(content_type__app_label='dataportal', codename__iregex=r'^add_').delete()

    print(f'All add permissions of {svc_user.username} user for dataportal models have been scraped')


class Migration(migrations.Migration):
    dependencies = [
        ('user_manage', '0002_add_default_users'),
    ]

    operations = [
        migrations.RunPython(add_permission, reverse_code=remove_permission),
    ]
