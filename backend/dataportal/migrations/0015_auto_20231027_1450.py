# Generated by Django 3.2.19 on 2023-10-27 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataportal', '0014_calibration_schedule_block_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calibration',
            name='delay_cal_id',
        ),
        migrations.RemoveField(
            model_name='calibration',
            name='phase_up_id',
        ),
    ]
