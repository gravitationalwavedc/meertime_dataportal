# Generated by Django 2.2.17 on 2021-09-23 12:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataportal', '0011_auto_20210906_1215'),
        ('web_cache', '0019_auto_20210831_0514'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foldpulsar',
            options={'ordering': ['-latest_observation']},
        ),
        migrations.AlterModelOptions(
            name='foldpulsardetail',
            options={'ordering': ['-utc']},
        ),
        migrations.AlterModelOptions(
            name='searchmodepulsar',
            options={'ordering': ['-latest_observation']},
        ),
        migrations.AlterModelOptions(
            name='searchmodepulsardetail',
            options={'ordering': ['-utc']},
        ),
        migrations.CreateModel(
            name='SessionPulsar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('backendSN', models.IntegerField()),
                ('intergrations', models.IntegerField()),
                ('frequency', models.DecimalField(decimal_places=8, max_digits=50)),
                ('phase_vs_time', models.URLField(null=True)),
                ('phase_vs_frequency', models.URLField(null=True)),
                ('profile', models.URLField(null=True)),
                ('fold_pulsar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_cache.FoldPulsar')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataportal.Sessions')),
            ],
        ),
    ]
