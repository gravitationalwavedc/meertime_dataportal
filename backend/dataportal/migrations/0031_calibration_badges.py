# Generated by Django 4.2.7 on 2024-04-23 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0030_alter_pipelineimage_image_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="calibration",
            name="badges",
            field=models.ManyToManyField(to="dataportal.badge"),
        ),
    ]
