# Generated by Django 2.2.17 on 2021-11-09 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_cache', '0030_auto_20211109_0229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionpulsar',
            name='backendSN',
            field=models.IntegerField(null=True),
        ),
    ]
