# Generated by Django 2.2.17 on 2021-12-01 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web_cache", "0040_auto_20211121_2253"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foldpulsar",
            name="jname",
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name="searchmodepulsar",
            name="jname",
            field=models.CharField(max_length=64),
        ),
    ]
