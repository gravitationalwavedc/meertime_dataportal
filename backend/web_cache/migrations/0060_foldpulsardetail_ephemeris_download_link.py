# Generated by Django 2.2.17 on 2022-12-01 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web_cache", "0059_auto_20221110_0334"),
    ]

    operations = [
        migrations.AddField(
            model_name="foldpulsardetail",
            name="ephemeris_download_link",
            field=models.URLField(null=True),
        ),
    ]