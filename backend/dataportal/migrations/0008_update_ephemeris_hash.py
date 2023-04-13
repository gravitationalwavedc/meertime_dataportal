import json
import hashlib

from django.db import migrations


def add_hash(apps, schema_editor):
    Ephemerides = apps.get_model("dataportal", "Ephemerides")

    objs = Ephemerides.objects.all()

    for obj in objs:
        obj.ephemeris_hash = hashlib.md5(
            json.dumps(obj.ephemeris, sort_keys=True, indent=2).encode("utf-8")
        ).hexdigest()
        obj.save()


def reverse_add_hash(apps, schema_editor):
    Ephemerides = apps.get_model("dataportal", "Ephemerides")

    objs = Ephemerides.objects.all()

    for obj in objs:
        obj.ephemeris_hash = None
        obj.save()


class Migration(migrations.Migration):
    dependencies = [("dataportal", "0007_ephemerides_ephemeris_hash")]

    operations = [migrations.RunPython(add_hash, reverse_code=reverse_add_hash)]
