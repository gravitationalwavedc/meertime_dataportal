# Generated by Django 2.2.17 on 2021-10-11 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web_cache", "0025_auto_20211011_2344"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foldpulsardetail",
            name="length",
            field=models.FloatField(null=True),
        ),
    ]
