from tqdm import tqdm
from web_cache.models import FoldPulsar, FoldPulsarDetail, SearchmodePulsar, SearchmodePulsarDetail, SessionPulsar
from dataportal.models import Foldings, Filterbankings, Sessions


def sync_foldmode():
    FoldPulsarDetail.objects.all().delete()
    FoldPulsar.objects.all().delete()

    for folding in tqdm(Foldings.objects.all()):
        folding.save()


def sync_searchmode():
    SearchmodePulsar.objects.all().delete()
    SearchmodePulsarDetail.objects.all().delete()

    for filter_bankings in tqdm(Filterbankings.objects.all()):
        filter_bankings.save()


def sync_sessions():
    SessionPulsar.objects.all().delete()

    print("Syncing SessionPulsar...")
    for session in tqdm(Sessions.objects.all()):
        session.save()
