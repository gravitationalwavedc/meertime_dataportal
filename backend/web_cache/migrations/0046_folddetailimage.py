# Generated by Django 2.2.17 on 2022-02-15 02:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web_cache', '0045_remove_foldpulsardetail_frequency_hi'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoldDetailImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('process', models.CharField(max_length=255)),
                ('image_type', models.CharField(max_length=64, null=True)),
                ('url', models.URLField()),
                ('fold_pulsar_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_cache.FoldPulsarDetail')),
            ],
        ),
    ]
