# Generated by Django 3.2.19 on 2023-11-24 07:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0017_auto_20231123_0240"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="residual",
            name="ephemeris",
        ),
        migrations.RemoveField(
            model_name="residual",
            name="project",
        ),
        migrations.RemoveField(
            model_name="residual",
            name="pulsar",
        ),
        migrations.AddField(
            model_name="toa",
            name="observation",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="toas",
                to="dataportal.observation",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="toa",
            name="project",
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to="dataportal.project"),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="toa",
            constraint=models.UniqueConstraint(
                fields=(
                    "observation",
                    "project",
                    "dm_corrected",
                    "obs_nchan",
                    "chan",
                    "minimum_nsubs",
                    "maximum_nsubs",
                    "subint",
                ),
                name="Unique ToA for observations, project and type of ToA (decimations).",
            ),
        ),
    ]
