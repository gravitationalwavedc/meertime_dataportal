# Generated by Django 2.2.24 on 2021-09-28 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataportal', '0011_auto_20210906_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toas',
            name='site',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]