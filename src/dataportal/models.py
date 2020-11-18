from django.db import models
from django.db.models import (
    Max,
    Min,
    F,
    ExpressionWrapper,
    DurationField,
    Count,
    Sum,
    Avg,
    OuterRef,
    Subquery,
    FloatField,
)
from django.db.models.functions import Sqrt, Ceil
from django.apps import apps
from .logic import get_band, get_band_filters, get_meertime_filters
from .storage import OverwriteStorage, get_upload_location

import logging

from datetime import timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False


class Schedule(models.Model):
    schedule = models.TextField()


class PhaseUp(models.Model):
    phaseup = models.TextField()


class Observations(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    utc = models.ForeignKey("Utcs", models.DO_NOTHING)
    proposal = models.ForeignKey("Proposals", models.DO_NOTHING, blank=True, null=True)
    beam = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    bw = models.FloatField(blank=True, null=True)
    frequency = models.FloatField(blank=True, null=True)
    rm_pipe = models.FloatField(db_column="RM_pipe", blank=True, null=True)
    dm_pipe = models.FloatField(db_column="DM_pipe", blank=True, null=True)
    dm_fold = models.FloatField(db_column="DM_fold", blank=True, null=True)
    nchan = models.IntegerField(blank=True, null=True)
    nbin = models.IntegerField(blank=True, null=True)
    nsubint = models.IntegerField(blank=True, null=True)
    mjd = models.TextField(db_column="MJD", blank=True, null=True)
    mjd_int = models.IntegerField(db_column="MJD_INT", blank=True, null=True)
    mjd_frac = models.TextField(db_column="MJD_frac", blank=True, null=True)
    pa = models.FloatField(db_column="PA", blank=True, null=True)
    observer = models.TextField(blank=True, null=True)
    snr_pipe = models.FloatField(db_column="SNR_pipe", blank=True, null=True)
    snr_spip = models.FloatField(db_column="SNR_spip", blank=True, null=True)
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)

    # these are the actual pointing coordinates which may be different from source coordinates.
    ra = models.TextField(db_column="RA", blank=True, null=True)
    dec = models.TextField(db_column="DEC", blank=True, null=True)

    # metadata describing which schedule block / observing session was this observation a part of
    # note that phase up is only relevant for interferometric observations
    schedule = models.ForeignKey("Schedule", on_delete=models.DO_NOTHING, null=True)
    phaseup = models.ForeignKey("PhaseUp", on_delete=models.DO_NOTHING, null=True)

    # plots
    profile = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    phase_vs_time = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    phase_vs_frequency = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    bandpass = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    snr_vs_time = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())

    @property
    def band(self):
        return get_band(self.frequency)

    class Meta:
        db_table = "Observations"
        unique_together = (("pulsar", "utc", "beam"),)

    @classmethod
    def get_last_session_by_gap(cls, max_gap=3600.0, get_proposal_filters=get_meertime_filters):
        """
        Get last observing session as determined by a gap between observations
        get_proposal_filters is a method which returns a set of observation filters
        max_gap is the maximum allowed gap between observations in seconds which defaults to one hour. Must be positive
        """
        proposal_filter = get_proposal_filters("proposal")
        latest_observations = (
            cls.objects.filter(**proposal_filter).values("id", "utc__utc_ts", "length").order_by("-utc__utc_ts")
        )

        if latest_observations.count() < 2:
            return latest_observations

        # latest observation is always in the latest session
        observation_ids = [latest_observations[0]["id"]]
        latest_included_utc = latest_observations[0]["utc__utc_ts"]

        for observation in latest_observations[1:]:
            gap = latest_included_utc - (observation["utc__utc_ts"] + timedelta(seconds=int(observation["length"])))
            if gap.seconds > max_gap:
                # we found all observations in the session
                break

            observation_ids.append(observation["id"])
            latest_included_utc = observation["utc__utc_ts"]

        return (
            cls.objects.select_related("utc", "pulsar", "proposal")
            .filter(id__in=observation_ids)
            .order_by("-utc__utc_ts")
        )


def get_observations_summary(qs):
    """
    This method operates on a query set of Observations and returns a summary of the query set as a dictionary.
    It is intended to operate on the results of the queryset as produced by get_last_session_by_gap but may be suitable
    for many observation querysets if deemed useful.
    """

    if not qs:
        return None

    # before getting a grouped by aggregate, we need to clear ordering otherwise some operations may work differently
    # than expected in particular values().annotate() does not work if the queryset was ordered. Even if we didn't
    # order the qs above, it may have come to us ordered already
    qs.query.clear_ordering(force_empty=True)
    projects = qs.values(project=F("proposal__proposal_short")).annotate(nobs=Count("id"))

    qs = qs.order_by("utc__utc_ts")
    offset = 0
    if qs.last().length:
        offset = qs.last().length

    return {
        "first": qs.first().utc.utc_ts,
        "last": qs.last().utc.utc_ts + timedelta(seconds=offset),
        "nobs": qs.count(),
        "npsr": qs.values("pulsar").distinct().count(),
        "projects": projects,
    }


class Proposals(models.Model):
    proposal = models.TextField(blank=True, null=True)
    proposal_short = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "Proposals"


class Ephemerides(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    updated_at = models.DateTimeField()
    # We'll store the ephemerides as JSON but in a TextField. This is to avoid the json getting normalised and losing the order of parameters.
    ephemeris = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "Ephemerides"


class Pulsars(models.Model):
    jname = models.TextField(db_column="Jname", blank=True, null=True)
    ephemeris = models.ForeignKey("Ephemerides", models.SET_NULL, null=True)
    state = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.jname}"

    @classmethod
    def get_observations(cls, mode, proposal=None, band=None, get_proposal_filters=get_meertime_filters):
        try:
            __class = apps.get_model("dataportal", mode.capitalize())
        except LookupError:
            logging.error(f"Mode {mode} does not correspond to any existing model in get_observation")
            return None

        observation_filter = get_proposal_filters(prefix="proposal")

        if proposal:
            observation_filter["proposal_id"] = proposal

        if band:
            observation_filter.update(get_band_filters(band))

        latest_observation = __class.objects.filter(pulsar=OuterRef("id"), **observation_filter).order_by(
            "-utc__utc_ts"
        )

        annotations = {
            "last": Max(f"{mode}__utc__utc_ts"),
            "last_beam": Subquery(latest_observation.values("beam")[:1]),
            "first": Min(f"{mode}__utc__utc_ts"),
            "proposal_short": Subquery(latest_observation.values("proposal__proposal_short")[:1]),
            "timespan": ExpressionWrapper(
                Max(f"{mode}__utc__utc_ts") - Min(f"{mode}__utc__utc_ts"), output_field=DurationField()
            ),
            "nobs": Count(f"{mode}"),
            "total_tint_h": Sum(f"{mode}__length") / 60 / 60,
        }
        # only use these for fold mode data
        if mode == "observations":
            foldmode_annotations = {
                "avg_snr_5min": Avg(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                "max_snr_5min": Max(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                "latest_snr": Subquery(latest_observation.values("snr_spip")[:1]),
                "latest_tint_m": Subquery(latest_observation.values("length")[:1]) / 60,
            }
            annotations.update(foldmode_annotations)

        obstype_filter = {f"{mode}__isnull": False}

        pulsar_proposal_filter = get_proposal_filters(prefix=f"{mode}__proposal")
        if proposal:
            pulsar_proposal_filter[f"{mode}__proposal__id"] = proposal

        if band:
            pulsar_proposal_filter.update(get_band_filters(band=band, prefix=mode))

        return (
            cls.objects.filter(**obstype_filter, **pulsar_proposal_filter)
            .values("jname", "id")
            .annotate(**annotations)
            .order_by("-last")
        )

    def observations_detail_data(self, get_proposal_filters=get_meertime_filters):
        proposal_filter = get_proposal_filters(prefix="proposal")
        # Stakeholders requested we display estimated disk size of data.
        # Unfortunately, we haven't been recording it nor all the necessary information to calculate it.
        # Therefore, I calculate it below using assumptions which are true for meertime data but will not
        # necessarily be true for other telescopes/instruments/projects. We will start ingesting required data
        # but for now we use this workaround:
        # nbit = 16 => 16.0/ 8.0 is conversion from bits to bytes
        # npol = 4 => * 4
        # subintegrations are 8s long, therefore nsubint = ceil(length/8)
        annotations = {
            "estimated_size": ExpressionWrapper(
                F("nchan") * F("nbin") * 4 * 16.0 / 8.0 * Ceil(F("length") / 8.0), output_field=FloatField()
            ),
            "proposal_short": F("proposal__proposal_short"),
        }
        return (
            self.observations_set.select_related("utc", "proposal")
            .filter(**proposal_filter)
            .annotate(**annotations)
            .order_by("-utc__utc_ts")
        )

    def searchmode_detail_data(self, get_proposal_filters=get_meertime_filters):
        proposal_filter = get_proposal_filters(prefix="proposal")
        return (
            self.searchmode_set.all()
            .select_related("utc", "proposal")
            .filter(**proposal_filter)
            .order_by("-utc__utc_ts")
        )

    class Meta:
        db_table = "Pulsars"


class Searchmode(models.Model):
    pulsar = models.ForeignKey(Pulsars, models.DO_NOTHING)
    utc = models.ForeignKey("Utcs", models.DO_NOTHING)
    proposal = models.ForeignKey(Proposals, models.DO_NOTHING, blank=True, null=True)
    beam = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    tsamp = models.FloatField(blank=True, null=True)
    bw = models.FloatField(blank=True, null=True)
    frequency = models.FloatField(blank=True, null=True)
    nchan = models.IntegerField(blank=True, null=True)
    nbit = models.IntegerField(blank=True, null=True)
    npol = models.IntegerField(blank=True, null=True)
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)
    dm = models.FloatField(db_column="DM", blank=True, null=True)
    ra = models.TextField(db_column="RA", blank=True, null=True)
    dec = models.TextField(db_column="DEC", blank=True, null=True)
    schedule = models.ForeignKey("Schedule", on_delete=models.DO_NOTHING, null=True)
    phaseup = models.ForeignKey("PhaseUp", on_delete=models.DO_NOTHING, null=True)

    @property
    def band(self):
        return get_band(self.frequency)

    class Meta:
        db_table = "Searchmode"
        unique_together = (("pulsar", "utc", "beam"),)


class Fluxcal(models.Model):
    pulsar = models.ForeignKey(Pulsars, models.DO_NOTHING)
    utc = models.ForeignKey("Utcs", models.DO_NOTHING)
    proposal = models.ForeignKey(Proposals, models.DO_NOTHING, blank=True, null=True)
    beam = models.IntegerField()
    comment = models.TextField(blank=True, null=True, default=None)
    length = models.FloatField(blank=True, null=True)
    bw = models.FloatField(blank=True, null=True)
    frequency = models.FloatField(blank=True, null=True)
    nchan = models.IntegerField(blank=True, null=True)
    nbin = models.IntegerField(blank=True, null=True)
    nsubint = models.IntegerField(blank=True, null=True)
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)
    snr_spip = models.FloatField(blank=True, null=True)
    schedule = models.ForeignKey("Schedule", on_delete=models.DO_NOTHING, null=True)
    phaseup = models.ForeignKey("PhaseUp", on_delete=models.DO_NOTHING, null=True)

    @property
    def band(self):
        return get_band(self.frequency)

    class Meta:
        db_table = "Fluxcal"
        unique_together = (("pulsar", "utc", "beam"),)


class Utcs(models.Model):
    utc_ts = models.DateTimeField()
    annotation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.utc_ts.strftime("%Y-%m-%d-%H:%M:%S")

    class Meta:
        db_table = "UTCs"
