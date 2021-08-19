from django.db.models.signals import post_save
from django.dispatch import receiver
from dataportal.models import Pulsars, Foldings, Filterbankings
from web_cache.models import FoldPulsar, FoldPulsarDetail, SearchmodePulsar, SearchmodePulsarDetail


@receiver(post_save, sender=Pulsars)
def handle_pulsars_save(sender, instance, **kwargs):
    if Foldings.objects.filter(folding_ephemeris__pulsar=instance):
        FoldPulsar.update_or_create(instance)

    pulsar_targets = instance.pulsartargets_set.all()
    targets = [p.target for p in pulsar_targets]

    if Filterbankings.objects.filter(processing__observation__target__in=targets):
        SearchmodePulsar.update_or_create(instance)


@receiver(post_save, sender=Foldings)
def handle_foldings_save(sender, instance, **kwargs):
    if FoldPulsar.objects.filter(jname=instance.folding_ephemeris.pulsar.jname).exists():
        FoldPulsarDetail.update_or_create(instance)


@receiver(post_save, sender=Filterbankings)
def handle_filterbankings_save(sender, instance, **kwargs):
    if SearchmodePulsar.objects.filter(jname=instance.processing.observation.target.name).exists():
        SearchmodePulsarDetail.update_or_create(instance)
