import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dataportal", "0044_delete_pipelinefile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mainproject",
            name="telescope",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="main_projects",
                to="dataportal.telescope",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="main_project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="projects",
                to="dataportal.mainproject",
            ),
        ),
    ]
