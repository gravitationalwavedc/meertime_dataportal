from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from dataportal.models import FoldPulsarSummary, FoldPulsarResult, PipelineRun





@receiver(post_save, sender=PipelineRun)
def handle_fold_pulsar_summary_update(sender, instance, **kwargs):
    """
    Every time a PipelineRun is saved, we want to update the FoldPulsarSummary
    model so it accurately summaries all fold observations for that pulsar.
    """
    # Make a fold result if there isn't one already
    FoldPulsarResult.objects.get_or_create(
        observation=instance.observation,
        pulsar=instance.observation.pulsar,
        defaults={
            "pipeline_run": instance,
            "embargo_end_date": datetime.now() + instance.observation.project.embargo_period,
        },
    )
    FoldPulsarSummary.update_or_create(instance.observation.pulsar, instance.observation.project.main_project)

