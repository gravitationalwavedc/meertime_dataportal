# Generated by Django 4.2.7 on 2024-02-13 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0023_remove_toa_residual_toa_binary_orbital_phase_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="toa",
            name="day_of_year",
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name="toa",
            name="residual_phase",
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name="toa",
            name="residual_sec",
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name="toa",
            name="residual_sec_err",
            field=models.FloatField(null=True),
        ),
    ]
