# Generated by Django 2.2.17 on 2021-08-31 05:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web_cache', '0018_auto_20210831_0440'),
    ]

    operations = [
        migrations.RenameField(
            model_name='foldpulsardetail',
            old_name='bw_mhz',
            new_name='bw',
        ),
    ]
