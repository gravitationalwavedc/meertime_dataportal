import json
import hashlib

from django.db import migrations
from django.db.models import Min, Count


def remove_duplicate_hash_for_pulsars(apps, schema_editor):
    Ephemerides = apps.get_model("dataportal", "Ephemerides")
    Foldings = apps.get_model("dataportal", "Foldings")
    Toas = apps.get_model("dataportal", "Toas")

    duplicates = (
        Ephemerides.objects.values('pulsar', 'ephemeris_hash')
        .annotate(min_id=Min('id'), count_id=Count('id'))
        .filter(count_id__gt=1)
    )

    for duplicate in duplicates:
        # WARNING: this is an irreversible action
        # It removes a duplicate based on pulsar and ephemeris_hash

        min_eph = Ephemerides.objects.get(id=duplicate['min_id'])

        ephs = Ephemerides.objects \
            .filter(pulsar=duplicate['pulsar'], ephemeris_hash=duplicate['ephemeris_hash']) \
            .exclude(id=duplicate['min_id'])

        for eph in ephs:

            # replace ref to the ephimeris to the one which will not be deleted
            try:
                folding = Foldings.objects.get(folding_ephemeris=eph)
                folding.folding_ephemeris = min_eph
                folding.save()
            except Foldings.DoesNotExist:
                pass
            except Foldings.MultipleObjectsReturned:
                foldings = Foldings.objects.filter(folding_ephemeris=eph)
                [folding.delete() for folding in foldings if folding.id != foldings.last().id] 
                foldings = Foldings.objects.get(folding_ephemeris=eph)
                foldings.folding_ephemeris = min_eph
                foldings.save()

            # replace ref to the ephimeris to the one which will not be deleted
            try:
                toas = Toas.objects.get(timing_ephemeris=eph)
                toas.timing_ephemeris = min_eph
                toas.save()
            except Toas.DoesNotExist:
                pass

            # safe to delete now
            eph.delete()


def reverse_duplicates(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('dataportal', '0008_update_ephemeris_hash')
    ]

    operations = [
        migrations.RunPython(remove_duplicate_hash_for_pulsars, reverse_code=reverse_duplicates)
    ]
