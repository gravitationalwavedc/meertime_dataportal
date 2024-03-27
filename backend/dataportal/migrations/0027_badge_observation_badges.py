# Generated by Django 4.2.7 on 2024-03-27 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dataportal", "0026_alter_observation_band_alter_observationsummary_band_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Badge",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=32, unique=True)),
                ("description", models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name="observation",
            name="badges",
            field=models.ManyToManyField(to="dataportal.badge"),
        ),
    ]
