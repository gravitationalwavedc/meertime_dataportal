# Generated by Django 3.2.19 on 2023-11-24 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0018_auto_20231124_0741"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="toa",
            name="Unique ToA for observations, project and type of ToA (decimations).",
        ),
    ]