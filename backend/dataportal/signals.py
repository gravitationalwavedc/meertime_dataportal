import numpy as np
from django.db.models.signals import post_save
from django.dispatch import receiver

from dataportal.models import (
    Badge,
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


@receiver(post_save, sender=PipelineRun)
def handle_badge_creation(sender, instance, **kwargs):
    """
    Every time a PipelineRun is saved, create badges based on the results.
    """
    if instance.job_state != "Completed":
        # Only create badges for completed jobs
        return

    # RFI badge
    rfi_badge, created = Badge.objects.get_or_create(
        name="Strong RFI",
        description="Over 20% of RFI removed from observation",
    )
    if instance.percent_rfi_zapped > 0.2:
        instance.badges.add(rfi_badge)

    # RM badge
    rm_badge, created = Badge.objects.get_or_create(
        name="RM Drift",
        description="The Rotation Measure has drifted three weighted standard deviations from the weighted mean",
    )
    # Get median and std RM for the pulsar
    pfrs_of_pulsar = PulsarFoldResult.objects.filter(
        pulsar=instance.observation.pulsar,
        observation__project__main_project=instance.observation.project.main_project,
    )
    rm_and_rm_error = (
        pfrs_of_pulsar.exclude(pipeline_run__rm__isnull=True)
        .exclude(pipeline_run__rm_err__isnull=True)
        .values_list("pipeline_run__rm", "pipeline_run__rm_err")
    )
    if len(rm_and_rm_error) > 0:
        rms, rm_errors = zip(*rm_and_rm_error)
        rms_array = np.array(rms)
        rms_errors_array = np.array(rm_errors)
        # Calculate weighted mean and std
        rms_weights = 1 / (rms_errors_array**2)
        rms_weights /= np.sum(rms_weights)
        rm_mean = np.average(rms_array, weights=rms_weights)
        rm_std = np.sqrt(np.average((rms_array - rm_mean) ** 2, weights=rms_weights))
        # Loop over pipeline runs for the pulsar and check if they have the RM badge
        for pfr in pfrs_of_pulsar:
            pipeline_run = pfr.pipeline_run
            if pipeline_run.rm is None:
                # Skip pipeline runs with no RM
                continue
            if abs(pipeline_run.rm - rm_mean) > 3 * rm_std and rm_std != 0:
                pipeline_run.badges.add(rm_badge)
            else:
                pipeline_run.badges.remove(rm_badge)

    # DM badge
    dm_badge, created = Badge.objects.get_or_create(
        name="DM Drift",
        description="The DM has drifted away from the median DM of the pulsar enough to cause a dispersion of three profile bins",  # noqa
    )
    # Get median DM for the pulsar
    dms = sorted(pfrs_of_pulsar.exclude(pipeline_run__dm__isnull=True).values_list("pipeline_run__dm", flat=True))
    count = len(dms)
    middle = count // 2
    if count % 2 == 0:
        # If even number of elements, take average of middle two elements
        dm_median = (dms[middle - 1] + dms[middle]) / 2
    else:
        # If odd number of elements, take the middle element
        dm_median = dms[middle]
    # Loop over pipeline runs for the pulsar and check if they have the DM badge
    for pfr in pfrs_of_pulsar:
        pipeline_run = pfr.pipeline_run
        if pipeline_run.dm is None:
            # Skip pipeline runs with no DM
            continue
        # Get the duration os a bin in milliseconds
        bin_duration_ms = pipeline_run.observation.ephemeris.p0 / pipeline_run.observation.fold_nbin * 1000
        # Use this to calculate the DM required to cause a dispersion of one bin
        dm_dispersion = (
            bin_duration_ms
            * pipeline_run.observation.frequency**3
            / (8.3 * 10.0**6 * pipeline_run.observation.bandwidth)
        )
        if abs(pipeline_run.dm - dm_median) > 3 * dm_dispersion:
            pipeline_run.badges.add(dm_badge)
        else:
            pipeline_run.badges.remove(dm_badge)
