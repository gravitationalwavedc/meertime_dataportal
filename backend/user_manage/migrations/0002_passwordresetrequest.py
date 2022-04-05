# Generated by Django 2.2.17 on 2022-03-31 12:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user_manage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResetRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('UNVERIFIED', 'UNVERIFIED'), ('VERIFIED', 'VERIFIED')], default='UNVERIFIED', max_length=55)),
                ('verification_code', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('verification_expiry', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
