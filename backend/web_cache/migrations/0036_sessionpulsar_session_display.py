# Generated by Django 2.2.17 on 2021-11-11 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web_cache', '0035_remove_sessionpulsar_session_display'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionpulsar',
            name='session_display',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='web_cache.SessionDisplay'),
            preserve_default=False,
        ),
    ]