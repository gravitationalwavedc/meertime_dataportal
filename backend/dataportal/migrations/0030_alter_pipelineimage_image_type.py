# Generated by Django 4.2.7 on 2024-04-19 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0029_merge_20240417_0216"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pipelineimage",
            name="image_type",
            field=models.CharField(
                choices=[
                    ("toa-single", "toa-single"),
                    ("profile", "profile"),
                    ("profile-pol", "profile-pol"),
                    ("phase-time", "phase-time"),
                    ("phase-freq", "phase-freq"),
                    ("bandpass", "bandpass"),
                    ("dynamic-spectrum", "dynamic-spectrum"),
                    ("snr-cumul", "snr-cumul"),
                    ("snr-single", "snr-single"),
                    ("rmfit", "rmfit"),
                ],
                max_length=16,
            ),
        ),
    ]