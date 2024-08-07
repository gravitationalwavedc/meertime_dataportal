# Generated by Django 4.2.7 on 2024-04-29 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0031_calibration_badges"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="toa",
            name="Unique ToA for observations, project and type of ToA (decimations).",
        ),
        migrations.RemoveField(
            model_name="toa",
            name="all_nsubs",
        ),
        migrations.RemoveField(
            model_name="toa",
            name="maximum_nsubs",
        ),
        migrations.RemoveField(
            model_name="toa",
            name="minimum_nsubs",
        ),
        migrations.RemoveField(
            model_name="toa",
            name="mode_nsubs",
        ),
        migrations.AddField(
            model_name="toa",
            name="nsub_type",
            field=models.CharField(
                choices=[("min", "min"), ("max", "max"), ("all", "all"), ("mode", "mode")], default="min", max_length=4
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="toa",
            constraint=models.UniqueConstraint(
                fields=(
                    "observation",
                    "project",
                    "dm_corrected",
                    "obs_npol",
                    "obs_nchan",
                    "chan",
                    "nsub_type",
                    "subint",
                ),
                name="Unique ToA for observations, project and type of ToA (decimations).",
            ),
        ),
    ]
