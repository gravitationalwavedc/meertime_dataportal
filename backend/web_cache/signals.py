from django.db.models.signals import post_save
from django.dispatch import receiver
from dataportal.models import Foldings, Filterbankings, Sessions
from web_cache.models import FoldPulsar, FoldPulsarDetail, SearchmodePulsar, SearchmodePulsarDetail, SessionPulsar


@receiver(post_save, sender=Foldings)
def handle_foldings_save(sender, instance, **kwargs):
    FoldPulsar.update_or_create(instance.folding_ephemeris.pulsar)
    FoldPulsarDetail.update_or_create(instance)


@receiver(post_save, sender=Filterbankings)
def handle_filterbankings_save(sender, instance, **kwargs):
    SearchmodePulsar.update_or_create(instance.processing.observation.target)
    SearchmodePulsarDetail.update_or_create(instance)


@receiver(post_save, sender=Sessions)
def handle_session_save(sender, instance, **kwargs):
    fold_pulsars = FoldPulsar.get_by_session(instance)
    for fold_pulsar in fold_pulsars:
        SessionPulsar.update_or_create(instance, fold_pulsar)

    searchmode_pulsars = SearchmodePulsar.get_by_session(instance)
    for searchmode_pulsar in searchmode_pulsars:
        SessionPulsar.update_or_create(instance, searchmode_pulsar)
