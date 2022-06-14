from tqdm import tqdm
from web_cache.models import (
    FoldPulsar,
    FoldPulsarDetail,
    SearchmodePulsar,
    SearchmodePulsarDetail,
    SessionPulsar,
    SessionDisplay,
)
from dataportal.models import Foldings, Filterbankings, Sessions, Pulsars, Targets, Programs


def sync_foldmode():
    """
    Sync the web application models with the pulsar database.

    First, remove all the existing web application model objects relating to fold mode. Next rebuild the FoldPulsar
    objects by looping through all the Pulsars and adding a FoldPulsar if it has a related folding ephmeris. We want to
    create one for each program so that we have a FoldPulsar object to attach observations to.
    """

    # We need to do the FoldPulsars first so that they're ready when the FoldPulsarDetail needs them.
    print("Syncing FoldPulsars")
    for pulsar in tqdm(Pulsars.objects.all()):
        # This is the way to tell if a Folding object relates to a particular pulsar.
        if Foldings.objects.filter(folding_ephemeris__pulsar=pulsar):
            # We want to create one for each program.
            # ToDo: Add a special 'All' program that doesn't filter observations by program.
            for program in Programs.objects.all():
                FoldPulsar.update_or_create(pulsar, program_name=program.name)

    print("Syncing FoldPulsarsDetails")
    for folding in tqdm(Foldings.objects.all()):
        FoldPulsarDetail.update_or_create(folding)


def sync_searchmode():
    SearchmodePulsar.objects.all().delete()
    SearchmodePulsarDetail.objects.all().delete()

    print("Syncing SearchmodePulsar")
    for target in tqdm(Targets.objects.all()):
        if Filterbankings.objects.filter(processing__observation__target=target):
            SearchmodePulsar.update_or_create(target)

    print("Syncing SearchmodePulsarDetails")
    for filter_bankings in tqdm(Filterbankings.objects.all()):
        SearchmodePulsarDetail.update_or_create(filter_bankings)


def sync_sessions():
    SessionDisplay.objects.all().delete()
    SessionPulsar.objects.all().delete()

    print("Syncing SessionPulsar")
    for session in tqdm(Sessions.objects.all()):
        SessionDisplay.update_or_create(session)
        session.save()
