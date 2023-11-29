# Generated by Django 3.2.19 on 2023-11-03 07:15

import dataportal.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataportal', '0015_auto_20231027_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='PipelineFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, storage=dataportal.storage.OverwriteStorage(), upload_to=dataportal.storage.get_upload_location)),
                ('file_type', models.CharField(choices=[('FTS', 'FTS')], max_length=16)),
                ('pulsar_fold_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='dataportal.pulsarfoldresult')),
            ],
        ),
        migrations.AddConstraint(
            model_name='pipelinefile',
            constraint=models.UniqueConstraint(fields=('pulsar_fold_result', 'file_type'), name='Unique file type for a PulsarFoldResult'),
        ),
    ]
