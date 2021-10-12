# Generated by Django 2.2.17 on 2021-10-12 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_cache', '0027_auto_20211012_0030'),
    ]

    operations = [
        migrations.RenameField(
            model_name='foldpulsardetail',
            old_name='bandpass',
            new_name='bandpass_hi',
        ),
        migrations.RenameField(
            model_name='foldpulsardetail',
            old_name='frequency',
            new_name='frequency_hi',
        ),
        migrations.RenameField(
            model_name='foldpulsardetail',
            old_name='phase_vs_frequency',
            new_name='phase_vs_frequency_hi',
        ),
        migrations.RenameField(
            model_name='foldpulsardetail',
            old_name='phase_vs_time',
            new_name='phase_vs_time_hi',
        ),
        migrations.RenameField(
            model_name='foldpulsardetail',
            old_name='profile',
            new_name='profile_hi',
        ),
        migrations.RenameField(
            model_name='foldpulsardetail',
            old_name='snr_vs_time',
            new_name='snr_vs_time_hi',
        ),
        migrations.RenameField(
            model_name='sessionpulsar',
            old_name='phase_vs_frequency',
            new_name='phase_vs_frequency_hi',
        ),
        migrations.RenameField(
            model_name='sessionpulsar',
            old_name='phase_vs_time',
            new_name='phase_vs_time_hi',
        ),
        migrations.RenameField(
            model_name='sessionpulsar',
            old_name='profile',
            new_name='profile_hi',
        ),
        migrations.AddField(
            model_name='foldpulsardetail',
            name='bandpass_lo',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='foldpulsardetail',
            name='frequency_lo',
            field=models.DecimalField(decimal_places=9, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='foldpulsardetail',
            name='phase_vs_frequency_lo',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='foldpulsardetail',
            name='phase_vs_time_lo',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='foldpulsardetail',
            name='profile_lo',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='foldpulsardetail',
            name='snr_vs_time_lo',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='sessionpulsar',
            name='phase_vs_frequency_lo',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='sessionpulsar',
            name='phase_vs_time_lo',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='sessionpulsar',
            name='profile_lo',
            field=models.URLField(null=True),
        ),
    ]
