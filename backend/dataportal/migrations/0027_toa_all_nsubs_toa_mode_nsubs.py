# Generated by Django 4.2.7 on 2024-04-11 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0026_alter_observation_band_alter_observationsummary_band_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="toa",
            name="all_nsubs",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="toa",
            name="mode_nsubs",
            field=models.BooleanField(default=False),
        ),
    ]
