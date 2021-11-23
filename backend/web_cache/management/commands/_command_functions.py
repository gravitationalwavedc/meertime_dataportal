from tqdm import tqdm
from web_cache.models import (
    FoldPulsar,
    FoldPulsarDetail,
    SearchmodePulsar,
    SearchmodePulsarDetail,
    SessionPulsar,
    SessionDisplay,
)
from dataportal.models import Foldings, Filterbankings, Sessions, Pulsars, Targets


def sync_foldmode():
    FoldPulsarDetail.objects.all().delete()
    FoldPulsar.objects.all().delete()

    print("Syncing FoldPulsars")
    for pulsar in tqdm(Pulsars.objects.filter()):
        if Foldings.objects.filter(folding_ephemeris__pulsar=pulsar):
            FoldPulsar.update_or_create(pulsar)

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
