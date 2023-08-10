from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from dataportal.models import PulsarFoldSummary, PulsarFoldResult, PipelineRun, Calibration, Observation, ObservationSummary



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
            "embargo_end_date": datetime.now() + instance.observation.project.embargo_period,
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

    # Update for the current values and each value with a None
    for obs_type in [instance.obs_type, None]:
        for pulsar in [instance.pulsar, None]:
            for telescope in [instance.telescope, None]:
                for project in [instance.project, None]:
                    for calibration in [instance.calibration, None]:
                        ObservationSummary.update_or_create(obs_type, pulsar, telescope, project, calibration)

