# Generated by Django 2.2.17 on 2022-02-10 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web_cache", "0043_auto_20220210_1059"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foldpulsar",
            name="main_project",
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name="searchmodepulsar",
            name="main_project",
            field=models.CharField(max_length=64),
        ),
    ]
