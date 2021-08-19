# Generated by Django 2.2.17 on 2021-08-16 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web_cache', '0007_auto_20210816_0317'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchmodePulsarDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utc', models.DateTimeField()),
                ('project', models.CharField(max_length=50)),
                ('ra', models.CharField(max_length=16)),
                ('dec', models.CharField(max_length=16)),
                ('length', models.DecimalField(decimal_places=1, max_digits=12)),
                ('beam', models.IntegerField()),
                ('frequency', models.DecimalField(decimal_places=8, max_digits=50)),
                ('nchan', models.IntegerField()),
                ('nbit', models.IntegerField()),
                ('nant_eff', models.IntegerField()),
                ('npol', models.IntegerField()),
                ('dm', models.DecimalField(decimal_places=2, max_digits=12)),
                ('tsamp', models.DecimalField(decimal_places=2, max_digits=12)),
                ('searchmode_pulsar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_cache.SearchmodePulsar')),
            ],
        ),
    ]
