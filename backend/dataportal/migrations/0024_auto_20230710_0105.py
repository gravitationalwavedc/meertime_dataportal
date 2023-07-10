# Generated by Django 3.2.19 on 2023-07-10 01:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataportal', '0023_alter_residual_mjd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='residual',
            name='toa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='toa', to='dataportal.toa'),
        ),
        migrations.AlterField(
            model_name='toa',
            name='pipeline_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='pipeline_run', to='dataportal.pipelinerun'),
        ),
    ]
