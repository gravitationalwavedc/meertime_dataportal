# Generated by Django 3.2.19 on 2023-05-18 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_cache', '0068_auto_20230518_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='foldpulsarfile',
            name='file_meta',
            field=models.CharField(max_length=64, null=True),
        ),
    ]