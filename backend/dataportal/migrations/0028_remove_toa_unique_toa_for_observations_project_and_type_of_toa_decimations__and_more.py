# Generated by Django 4.2.7 on 2024-04-11 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0027_toa_all_nsubs_toa_mode_nsubs"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="toa",
            name="Unique ToA for observations, project and type of ToA (decimations).",
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
                    "minimum_nsubs",
                    "maximum_nsubs",
                    "all_nsubs",
                    "mode_nsubs",
                    "subint",
                ),
                name="Unique ToA for observations, project and type of ToA (decimations).",
            ),
        ),
    ]
