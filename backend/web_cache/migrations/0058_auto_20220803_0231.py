# Generated by Django 2.2.17 on 2022-08-03 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web_cache", "0057_merge_20220712_0918"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foldpulsardetail",
            name="dm_meerpipe",
            field=models.DecimalField(decimal_places=4, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name="foldpulsardetail",
            name="rm_meerpipe",
            field=models.DecimalField(decimal_places=4, max_digits=12, null=True),
        ),
    ]
