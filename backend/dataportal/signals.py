from django.db.models.signals import post_save
from django.dispatch import receiver

from dataportal.models import (
    Calibration,
    Observation,
    ObservationSummary,
    PipelineRun,
    PulsarFoldResult,
    PulsarFoldSummary,
    PulsarSearchSummary,
)


@receiver(post_save, sender=PipelineRun)
def handle_pulsar_fold_summary_update(sender, instance, **kwargs):
    """
    Every time a PipelineRun is saved, we want to update the PulsarFoldSummary
    model so it accurately summaries all fold observations for that pulsar.
    """
    # Make a fold result if there isn't one already
    pulsar_fold_result, created = PulsarFoldResult.objects.get_or_create(
        observation=instance.observation,
        pulsar=instance.observation.pulsar,
        defaults={
            "pipeline_run": instance,
        },
    )
    if instance.job_state == "Completed":
        # Update the result foreign key to update the results
        pulsar_fold_result.pipeline_run = instance
        pulsar_fold_result.save()

    # Update the summary info
    PulsarFoldSummary.update_or_create(instance.observation.pulsar, instance.observation.project.main_project)


@receiver(post_save, sender=Observation)
def handle_calibration_update(sender, instance, **kwargs):
    """
    Every time a Observation is saved, we want to update the Calibration
    to summarise the session and the ObservationSummary.
    """
    Calibration.update_observation_session(instance.calibration)

    if instance.obs_type == "search":
        # Update the summary info (do this after the observation upload because there is no search pipeline products)
        PulsarSearchSummary.update_or_create(instance.pulsar, instance.project.main_project)

    if instance.obs_type == "fold":
        # Update fold summaries
        obs_type = "fold"
        main_project = instance.project.main_project
        calibration = None
        for pulsar in [instance.pulsar, None]:
            for project in [instance.project, None]:
                for band in [instance.band, None]:
                    ObservationSummary.update_or_create(obs_type, pulsar, main_project, project, calibration, band)
    elif instance.obs_type == "search":
        # Update search summaries
        obs_type = "search"
        main_project = instance.project.main_project
        calibration = None
        for pulsar in [instance.pulsar, None]:
            for project in [instance.project, None]:
                for band in [instance.band, None]:
                    ObservationSummary.update_or_create(obs_type, pulsar, main_project, project, calibration, band)
    # Always update calibration summaries
    obs_type = None
    pulsar = None
    main_project = None
    calibration = instance.calibration
    band = None
    for project in [instance.project, None]:
        ObservationSummary.update_or_create(obs_type, pulsar, main_project, project, calibration, band)
