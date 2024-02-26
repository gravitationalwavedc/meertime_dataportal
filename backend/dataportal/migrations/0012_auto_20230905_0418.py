# Generated by Django 3.2.19 on 2023-09-05 04:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0011_pulsarsearchsummary"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="observationsummary",
            name="telescope",
        ),
        migrations.AddField(
            model_name="observationsummary",
            name="band",
            field=models.CharField(
                choices=[
                    ("UHF", "UHF"),
                    ("LBAND", "LBAND"),
                    ("SBAND_0", "SBAND_0"),
                    ("SBAND_1", "SBAND_1"),
                    ("SBAND_2", "SBAND_2"),
                    ("SBAND_3", "SBAND_3"),
                    ("SBAND_4", "SBAND_4"),
                ],
                max_length=7,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="observationsummary",
            name="main_project",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="dataportal.mainproject"
            ),
        ),
    ]
