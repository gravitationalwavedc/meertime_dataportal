# Generated by Django 3.2.3 on 2023-02-23 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0014_auto_20220614_0052"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ephemerides",
            name="ephemeris",
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name="observations",
            name="config",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="pipelines",
            name="configuration",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="processings",
            name="job_output",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="processings",
            name="results",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="toas",
            name="flags",
            field=models.JSONField(),
        ),
    ]