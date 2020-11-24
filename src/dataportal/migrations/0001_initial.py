# Generated by Django 2.2.17 on 2020-11-24 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ephemerides',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('created_by', models.CharField(max_length=64)),
                ('ephemeris', models.TextField()),
                ('p0', models.DecimalField(decimal_places=8, max_digits=10)),
                ('dm', models.FloatField()),
                ('rm', models.FloatField()),
                ('comment', models.CharField(blank=True, max_length=255, null=True)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Foldings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nbin', models.IntegerField()),
                ('npol', models.IntegerField()),
                ('nchan', models.IntegerField()),
                ('dm', models.FloatField(blank=True, null=True)),
                ('tsubint', models.IntegerField()),
                ('folding_ephemeris', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Ephemerides')),
            ],
        ),
        migrations.CreateModel(
            name='Instrumentconfigs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bandwidth', models.DecimalField(decimal_places=6, max_digits=12)),
                ('frequency', models.DecimalField(decimal_places=9, max_digits=15)),
                ('nchan', models.IntegerField()),
                ('npol', models.IntegerField()),
                ('beam', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Observations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utc_start', models.DateTimeField()),
                ('duration', models.FloatField()),
                ('obs_type', models.CharField(max_length=8)),
                ('suspect', models.IntegerField()),
                ('comment', models.CharField(blank=True, max_length=255, null=True)),
                ('instrument_config', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Instrumentconfigs')),
            ],
        ),
        migrations.CreateModel(
            name='Pipelines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('revision', models.CharField(max_length=16)),
                ('created_at', models.DateTimeField()),
                ('created_by', models.CharField(max_length=64)),
                ('configuration', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Processings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
                ('job_state', models.CharField(blank=True, max_length=255, null=True)),
                ('job_output', models.TextField(blank=True, null=True)),
                ('results', models.TextField(blank=True, null=True)),
                ('observation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Observations')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings')),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Pipelines')),
            ],
        ),
        migrations.CreateModel(
            name='Ptusecalibrations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calibration_type', models.CharField(max_length=4)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pulsars',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jname', models.CharField(max_length=64)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('comment', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Targets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('raj', models.CharField(max_length=16)),
                ('decj', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Telescopes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Templates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.FloatField()),
                ('bandwidth', models.FloatField()),
                ('created_at', models.DateTimeField()),
                ('created_by', models.CharField(max_length=64)),
                ('location', models.CharField(max_length=255)),
                ('method', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('comment', models.CharField(blank=True, max_length=255, null=True)),
                ('pulsar', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Pulsars')),
            ],
        ),
        migrations.CreateModel(
            name='Toas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flags', models.TextField()),
                ('frequency', models.FloatField()),
                ('mjd', models.CharField(blank=True, max_length=32, null=True)),
                ('site', models.IntegerField(blank=True, null=True)),
                ('uncertainty', models.FloatField(blank=True, null=True)),
                ('valid', models.IntegerField(blank=True, null=True)),
                ('comment', models.CharField(blank=True, max_length=255, null=True)),
                ('input_folding', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Foldings')),
                ('processing', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Templates')),
                ('timing_ephemeris', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Ephemerides')),
            ],
        ),
        migrations.CreateModel(
            name='Rfis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent_zapped', models.FloatField()),
                ('folding', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Foldings')),
                ('processing', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings')),
            ],
        ),
        migrations.CreateModel(
            name='Pulsartargets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pulsar', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Pulsars')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Targets')),
            ],
        ),
        migrations.CreateModel(
            name='Pulsaraliases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=64)),
                ('pulsar', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Pulsars')),
            ],
        ),
        migrations.CreateModel(
            name='Ptuseconfigs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposal_id', models.CharField(max_length=32)),
                ('schedule_block_id', models.CharField(max_length=32)),
                ('experiment_id', models.CharField(max_length=32)),
                ('phaseup_id', models.CharField(blank=True, max_length=32, null=True)),
                ('delaycal_id', models.CharField(blank=True, max_length=32, null=True)),
                ('nant', models.IntegerField()),
                ('nant_eff', models.IntegerField()),
                ('configuration', models.TextField()),
                ('calibration', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Ptusecalibrations')),
                ('observation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Observations')),
            ],
        ),
        migrations.CreateModel(
            name='Processingcollections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Collections')),
                ('processing', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings')),
            ],
        ),
        migrations.CreateModel(
            name='Pipelineimages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('image_type', models.CharField(blank=True, max_length=64, null=True)),
                ('image', models.CharField(max_length=255)),
                ('processing', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings')),
            ],
        ),
        migrations.AddField(
            model_name='observations',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Targets'),
        ),
        migrations.AddField(
            model_name='observations',
            name='telescope',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Telescopes'),
        ),
        migrations.CreateModel(
            name='Launches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_pipeline', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='parent_pipeline', to='dataportal.Pipelines')),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Pipelines')),
                ('pulsar', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Pulsars')),
            ],
        ),
        migrations.AddField(
            model_name='foldings',
            name='processing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings'),
        ),
        migrations.CreateModel(
            name='Filterbankings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nbit', models.IntegerField()),
                ('npol', models.IntegerField()),
                ('nchan', models.IntegerField()),
                ('tsamp', models.FloatField()),
                ('dm', models.FloatField()),
                ('processing', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings')),
            ],
        ),
        migrations.AddField(
            model_name='ephemerides',
            name='pulsar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Pulsars'),
        ),
        migrations.CreateModel(
            name='Caspsrconfigs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.CharField(max_length=16)),
                ('configuration', models.TextField()),
                ('observation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Observations')),
            ],
        ),
        migrations.CreateModel(
            name='Basebandings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processing', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataportal.Processings')),
            ],
        ),
    ]
