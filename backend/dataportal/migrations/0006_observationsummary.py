# Generated by Django 3.2.19 on 2023-08-08 03:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataportal', '0005_alter_calibration_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObservationSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obs_type', models.CharField(choices=[('cal', 'cal'), ('fold', 'fold'), ('search', 'search')], max_length=6)),
                ('observations', models.IntegerField(blank=True, null=True)),
                ('pulsars', models.IntegerField(blank=True, null=True)),
                ('projects', models.IntegerField(blank=True, null=True)),
                ('estimated_disk_space_gb', models.FloatField(blank=True, null=True)),
                ('observation_hours', models.IntegerField(blank=True, null=True)),
                ('timespan_days', models.IntegerField(blank=True, null=True)),
                ('min_duration', models.FloatField(blank=True, null=True)),
                ('max_duration', models.FloatField(blank=True, null=True)),
                ('calibration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='observation_summaries', to='dataportal.calibration')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dataportal.project')),
                ('pulsar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dataportal.pulsar')),
                ('telescope', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dataportal.telescope')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
