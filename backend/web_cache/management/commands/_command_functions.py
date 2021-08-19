from tqdm import tqdm
from web_cache.models import FoldPulsar, FoldPulsarDetail, SearchmodePulsar
from dataportal.models import Pulsars, Foldings, Filterbankings


def sync_foldmode():
    FoldPulsarDetail.objects.all().delete()
    FoldPulsar.objects.all().delete()

    print("Syncing FoldPulsars...")
    for pulsar in tqdm(Pulsars.objects.all()):
        pulsar.save()

    print("Syncing FoldPulsarDetails...")
    for folding in tqdm(Foldings.objects.all()):
        folding.save()


def sync_searchmode():
    SearchmodePulsar.objects.all().delete()

    print("Syncing SearchmodePulsar...")
    for pulsar in tqdm(Pulsars.objects.all()):
        pulsar.save()

    print("Syncing SearchmodePulsarDetails...")
    for filter_bankings in tqdm(Filterbankings.objects.all()):
        filter_bankings.save()
