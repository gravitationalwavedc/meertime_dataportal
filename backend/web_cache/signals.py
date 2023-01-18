from contextlib import suppress
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from dataportal.models import Foldings, Filterbankings, Sessions, Pipelineimages, Pulsars
from web_cache.models import (
    FoldPulsar,
    FoldPulsarDetail,
    SearchmodePulsar,
    SearchmodePulsarDetail,
    SessionPulsar,
    SessionDisplay,
)

@receiver(post_save, sender=Pulsars)
def handle_pulsar_comment_update(sender, instance, **kwargs):
    # There's a very small chance that due to database updates by ingest there might be a pulsar 
    # but no FoldPulsar model. We don't really care about this because it'll be fixed the next time 
    # that the ingest runs.
    with suppress(FoldPulsar.DoesNotExist):
        fold_pulsar = FoldPulsar.objects.get(jname=instance.jname)
        fold_pulsar.comment = instance.comment
        fold_pulsar.save()


@receiver(post_save, sender=Foldings)
def handle_foldings_save(sender, instance, **kwargs):
    FoldPulsar.update_or_create(
        instance.folding_ephemeris.pulsar, program_name=instance.processing.observation.project.program.name
    )
    FoldPulsarDetail.update_or_create(instance)


@receiver(post_save, sender=Filterbankings)
def handle_filterbankings_save(sender, instance, **kwargs):
    SearchmodePulsar.update_or_create(instance.processing.observation.target)
    SearchmodePulsarDetail.update_or_create(instance)


@receiver(post_save, sender=Sessions)
def handle_session_save(sender, instance, **kwargs):
    session_display, _ = SessionDisplay.update_or_create(instance)

    fold_pulsars = FoldPulsar.get_by_session(instance)
    for fold_pulsar in fold_pulsars:
        SessionPulsar.update_or_create(session_display, fold_pulsar)

    searchmode_pulsars = SearchmodePulsar.get_by_session(instance)
    for searchmode_pulsar in searchmode_pulsars:
        SessionPulsar.update_or_create(session_display, searchmode_pulsar)

    # Run this again so that we can make sure the data is accurate.
    # It requires all the SessionPulsars to be processed first, but they also need a reference to a SessionDisplay
    session_display, _ = SessionDisplay.update_or_create(instance)


@receiver(post_save, sender=Pipelineimages)
def handle_image_save(sender, instance, **kwargs):
    for folding in instance.processing.foldings_set.all():
        FoldPulsarDetail.update_or_create(folding)


@receiver(post_delete, sender=Sessions)
def handle_session_delete(sender, instance, **kwargs):
    # There's a small chance that a Session may have been created by the ingest script but not have created 
    # a SessionDisplay in the web_cache. This gets fixed the next time the ingest runs or a sync_web_cache is called,
    # so we don't care about the error.
    with suppress(SessionDisplay.DoesNotExist):
        SessionDisplay.objects.get(start=instance.start, end=instance.end).delete()
