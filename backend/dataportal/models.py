import hashlib
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, OuterRef, Subquery, Max, Min, ExpressionWrapper, Count, Sum
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import ugettext_lazy as _
from django_mysql.models import Model
from django_mysql.models import JSONField
from .logic import get_meertime_filters, get_band
from json import loads
from datetime import timedelta
from .storage import OverwriteStorage, get_upload_location, get_pipeline_upload_location


class Basebandings(models.Model):
    # Note, this is intended as a 1-to-1 extension of the Processings table, sort of a "subclass" of the Processings
    processing = models.OneToOneField("Processings", models.DO_NOTHING)


class Calibrations(models.Model):
    CALIBRATION_TYPES = [
        ("pre", "pre"),
        ("post", "post"),
        ("none", "none"),
    ]
    calibration_type = models.CharField(max_length=4, choices=CALIBRATION_TYPES)
    location = models.CharField(max_length=255, blank=True, null=True)

    def save(cls, *args, **kwargs):
        # Enforce choices are respected
        cls.full_clean()
        return super(Calibrations, cls).save(*args, **kwargs)


class Collections(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, null=True)


class Ephemerides(models.Model):
    limits = {
        "p0": {"max": 10, "deci": 8},
    }
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    # TODO ephemeris is a bit of a problem. We'd like to have pulsar + ephemeris as a unique constraint.
    # But: if ephemeris is a JSONField then we can't use it as a constraint without specifying which keys are to be
    # used for the constraint (and I don't think we can support that via django). And if it's a Text or Char Field
    # then we need to specify max length and potentially run into issues with long ephemerides. Max is 3072 bytes
    # but we're defaulting to UTF-8 so that's 3 bytes per character and thus we could only use a 1024 character long
    # ephemeris which is not that long at all. For now, leaving as textfield and out of index as I don't know how to
    # work around this problem. To try and ensure this doens't cause issues, we use ephemeris in get_or_create
    # lookup but according to the docs, this does not guarantee there won't be duplicates without a unique
    # constraint here.
    ephemeris = JSONField()
    ephemeris_hash = models.CharField(max_length=32, editable=False, null=True)
    p0 = models.DecimalField(max_digits=limits["p0"]["max"], decimal_places=limits["p0"]["deci"])
    dm = models.FloatField()
    rm = models.FloatField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    valid_from = models.DateTimeField()
    # we should be making sure valid_to is later than valid_from
    valid_to = models.DateTimeField()

    class Meta:
        unique_together = [['pulsar', 'ephemeris_hash']]

    def clean(self, *args, **kwargs):
        # checking valid_to is later than valid_from
        if self.valid_from >= self.valid_to:
            raise ValidationError(_('valid_to must be later than valid_from'))

    def save(self, *args, **kwargs):
        Ephemerides.clean(self)
        self.ephemeris_hash = hashlib.md5(
            json.dumps(self.ephemeris, sort_keys=True, indent=2).encode("utf-8")
        ).hexdigest()
        super(Ephemerides, self).save(*args, **kwargs)


class Filterbankings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    nbit = models.IntegerField()
    npol = models.IntegerField()
    nchan = models.IntegerField()
    tsamp = models.FloatField()
    dm = models.FloatField()


class Foldings(models.Model):
    # Note, this is intended as a 1-to-1 extension of the Processings table, sort of a "subclass" of the Processings
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    folding_ephemeris = models.ForeignKey("Ephemerides", models.DO_NOTHING)
    nbin = models.IntegerField()
    npol = models.IntegerField()
    nchan = models.IntegerField()
    dm = models.FloatField(blank=True, null=True)
    tsubint = models.FloatField()

    class Meta:
        constraints = [UniqueConstraint(fields=["processing"], name="unique folding")]

    @property
    def band(cls):
        freq = cls.processing.observation.instrument_config.frequency
        return get_band(float(freq))

    @classmethod
    def get_observation_details(cls, pulsar, utc, beam):
        annotations = {
            "jname": F("folding_ephemeris__pulsar__jname"),
            "utc": F("processing__observation__utc_start"),
            "beam": F("processing__observation__instrument_config__beam"),
            "proposal": F("processing__observation__project__code"),
            "frequency": F("processing__observation__instrument_config__frequency"),
            "bw": F("processing__observation__instrument_config__bandwidth"),
            "ra": F("processing__observation__target__raj"),
            "dec": F("processing__observation__target__decj"),
            "duration": F("processing__observation__duration"),
            "results": F("processing__results"),
            "nant": F("processing__observation__nant"),
            "nant_eff": F("processing__observation__nant_eff"),
            "config": F("processing__observation__config"),
        }

        return (
            cls.objects.select_related(
                "processing__observation__instrument_config",
                "folding_ephemeris__pulsar",
                "processing__observation__project",
                "processing__observation__target",
            )
            .filter(
                folding_ephemeris__pulsar=pulsar,
                processing__observation__utc_start=utc,
                processing__observation__instrument_config__beam=beam,
            )
            .annotate(**annotations)
            .first()
        )


class Instrumentconfigs(models.Model):
    limits = {"bandwidth": {"max": 12, "deci": 6}, "frequency": {"max": 15, "deci": 9}}
    name = models.CharField(max_length=255)
    bandwidth = models.DecimalField(max_digits=limits["bandwidth"]["max"], decimal_places=limits["bandwidth"]["deci"])
    frequency = models.DecimalField(max_digits=limits["frequency"]["max"], decimal_places=limits["frequency"]["deci"])
    nchan = models.IntegerField()
    npol = models.IntegerField()
    beam = models.CharField(max_length=16)


class Launches(models.Model):
    pipeline = models.ForeignKey("Pipelines", models.DO_NOTHING)
    parent_pipeline = models.ForeignKey(
        "Pipelines", models.DO_NOTHING, blank=True, null=True, related_name="parent_pipeline"
    )
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)


class Observations(models.Model):
    target = models.ForeignKey("Targets", models.DO_NOTHING)
    calibration = models.ForeignKey("Calibrations", models.DO_NOTHING, null=True)
    telescope = models.ForeignKey("Telescopes", models.DO_NOTHING)
    instrument_config = models.ForeignKey("Instrumentconfigs", models.DO_NOTHING)
    project = models.ForeignKey("Projects", models.DO_NOTHING)
    config = JSONField(blank=True, null=True)
    utc_start = models.DateTimeField()
    duration = models.FloatField(null=True)
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)
    suspect = models.BooleanField(default=False)
    comment = models.CharField(max_length=255, blank=True, null=True)


class Projects(models.Model):
    program = models.ForeignKey("Programs", models.DO_NOTHING, null=True)
    default_embargo = timedelta(days=548)  # 18 months default embargo

    code = models.CharField(max_length=255, unique=True)
    short = models.CharField(max_length=20, default="???")
    embargo_period = models.DurationField(default=default_embargo)
    description = models.CharField(max_length=255, blank=True, null=True)


class Pipelineimages(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    rank = models.IntegerField()
    image_type = models.CharField(max_length=64, blank=True, null=True)
    image = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())

    class Meta:
        constraints = [
            UniqueConstraint(fields=["processing", "image_type"], name="unique image type for a processing")
        ]


class Pipelinefiles(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    file = models.FileField(null=True, upload_to=get_pipeline_upload_location, storage=OverwriteStorage())
    file_type = models.CharField(max_length=32, blank=True, null=True)


class Pipelines(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, null=True)
    revision = models.CharField(max_length=16)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    configuration = JSONField(blank=True, null=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["name", "revision"], name="unique pipeline")]


class Processingcollections(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    collection = models.ForeignKey(Collections, models.DO_NOTHING)


class Processings(Model):
    observation = models.ForeignKey(Observations, models.DO_NOTHING)
    pipeline = models.ForeignKey(Pipelines, models.DO_NOTHING)
    parent = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    embargo_end = models.DateTimeField()
    location = models.CharField(max_length=255)
    job_state = models.CharField(max_length=255, blank=True, null=True)
    job_output = JSONField(blank=True, null=True)
    # TODO we would like to use results as part of the unique constraint but same problem as in the ephemeris class (see the comment there)
    results = JSONField(blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["observation", "pipeline", "location", "parent"], name="unique processing")
        ]


class Programs(Model):
    telescope = models.ForeignKey("Telescopes", models.DO_NOTHING)
    name = models.CharField(max_length=64)


class Pulsaraliases(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    alias = models.CharField(max_length=64)


class Pulsartargets(models.Model):
    target = models.ForeignKey("Targets", models.DO_NOTHING)
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)


class Pulsars(models.Model):
    jname = models.CharField(max_length=64, unique=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)

    # These look like the Searchmode
    def get_observations_for_pulsar(cls, get_proposal_filters=get_meertime_filters):
        folding_filter = get_proposal_filters(prefix="processing__observation")

        annotations = {
            "utc": F("processing__observation__utc_start"),
            "bw": F("processing__observation__instrument_config__bandwidth"),
            "length": F("processing__observation__duration"),
            "proposal": F("processing__observation__project__short"),
            "beam": F("processing__observation__instrument_config__beam"),
            "nant": F("processing__observation__nant"),
            "nant_eff": F("processing__observation__nant_eff"),
            "results": F("processing__results"),
        }

        folds = (
            Foldings.objects.select_related("processing__observation__instrument_config")
            .filter(folding_ephemeris__pulsar=cls, **folding_filter)
            .annotate(**annotations)
        )
        return folds.order_by("-utc")
        # Get various related model objects required using the saved folding instance as a base.
        # latest_folding_observation = (
        #     Foldings.objects.filter(folding_ephemeris__pulsar=pulsar)
        #     .order_by("-processing__observation__utc_start")
        #     .last()
        # )

    # These look like the Fold Mode
    @classmethod
    def get_latest_observations(cls, get_proposal_filters=get_meertime_filters):
        folding_filter = get_proposal_filters(prefix="processing__observation")

        latest_observation = Foldings.objects.filter(
            folding_ephemeris__pulsar=OuterRef("id"), **folding_filter
        ).order_by("-processing__observation__utc_start")

        annotations = {
            "last": Max("pulsartargets__target__observations__utc_start"),
            "first": Min("pulsartargets__target__observations__utc_start"),
            "timespan": ExpressionWrapper(
                Max("pulsartargets__target__observations__utc_start")
                - Min("pulsartargets__target__observations__utc_start")
                + 1,
                output_field=models.DurationField(),
            ),
            "nobs": Count("pulsartargets__target__observations"),
            "length": Subquery(latest_observation.values("processing__observation__duration")[:1]) / 60.0,
            "total_tint_h": Sum("pulsartargets__target__observations__duration") / 60.0 / 60.0,
            "proposal_short": Subquery(latest_observation.values("processing__observation__project__short")[:1]),
            "snr": Subquery(latest_observation.values("processing__results__snr")[:1]),
            "beam": Subquery(latest_observation.values("processing__observation__instrument_config__beam")[:1]),
        }

        pulsar_proposal_filter = get_proposal_filters(prefix="pulsartargets__target__observations")
        # since ingest is now done in stages, it can happen that an observation won't have the beam set properly so we
        # need to filter empty beams not to trip up the obs_detail url lookup
        # this can happen if an observation is created, is the latest observation, but no corresponding
        # processing/folding was created yet
        return (
            cls.objects.values("jname", "id")
            .filter(**pulsar_proposal_filter)
            .annotate(**annotations)
            .order_by("-last")
            .exclude(beam__isnull=True)
        )


class Rfis(models.Model):
    # Note, this is intended as a 1-to-1 extension of the Processings table, sort of a "subclass" of the Processings
    processing = models.ForeignKey(Processings, models.DO_NOTHING)
    folding = models.ForeignKey(Foldings, models.DO_NOTHING)
    percent_zapped = models.FloatField()


class Sessions(models.Model):
    telescope = models.ForeignKey("Telescopes", models.DO_NOTHING)
    start = models.DateTimeField()
    end = models.DateTimeField()


class Targets(models.Model):
    name = models.CharField(max_length=64)
    raj = models.CharField(max_length=16)
    decj = models.CharField(max_length=16)

    class Meta:
        constraints = [UniqueConstraint(fields=["name", "raj", "decj"], name="unique target")]


class Telescopes(models.Model):
    name = models.CharField(max_length=64, unique=True)


class Templates(models.Model):
    pulsar = models.ForeignKey(Pulsars, models.DO_NOTHING)
    frequency = models.FloatField()
    bandwidth = models.FloatField()
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    location = models.CharField(max_length=255)
    method = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)


class Toas(models.Model):
    QUALITY_CHOICES = [("nominal", "nominal"), ("bad", "bad")]

    processing = models.ForeignKey(Processings, models.DO_NOTHING)
    input_folding = models.ForeignKey(Foldings, models.DO_NOTHING)
    timing_ephemeris = models.ForeignKey(Ephemerides, models.DO_NOTHING, null=True)
    template = models.ForeignKey(Templates, models.DO_NOTHING)
    flags = JSONField()
    frequency = models.FloatField()
    mjd = models.CharField(max_length=32, blank=True, null=True)
    site = models.CharField(max_length=1, blank=True, null=True)
    uncertainty = models.FloatField(blank=True, null=True)
    quality = models.CharField(max_length=7, blank=True, null=True, choices=QUALITY_CHOICES)
    comment = models.CharField(max_length=255, blank=True, null=True)
