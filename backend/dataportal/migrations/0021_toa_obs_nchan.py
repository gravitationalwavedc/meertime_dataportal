# Generated by Django 3.2.19 on 2023-07-05 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataportal', '0020_auto_20230705_0406'),
    ]

    operations = [
        migrations.AddField(
            model_name='toa',
            name='obs_nchan',
            field=models.IntegerField(null=True),
        ),
    ]
