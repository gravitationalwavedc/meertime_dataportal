# Generated by Django 4.2.7 on 2024-03-28 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0027_badge_observation_badges"),
    ]

    operations = [
        migrations.AddField(
            model_name="pipelinerun",
            name="badges",
            field=models.ManyToManyField(to="dataportal.badge"),
        ),
    ]