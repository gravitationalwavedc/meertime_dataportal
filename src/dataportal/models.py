from django.db import models
from django.db.models import F
from django_mysql.models import Model
from django_mysql.models import JSONField
from .logic import get_meertime_filters, get_band
from json import loads
from datetime import timedelta


class Basebandings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)


class Calibrations(models.Model):
    CALIBRATION_TYPES = [
        ("pre", "pre"),
        ("post", "post"),
        ("none", "none"),
    ]
    calibration_type = models.CharField(max_length=4, choices=CALIBRATION_TYPES)
    location = models.CharField(max_length=255, blank=True, null=True)


class Collections(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, null=True)


class Ephemerides(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    # Keeping this as a text field for now, to avoid having to reformat the ephemeris when displaying
    ephemeris = models.TextField()
    p0 = models.DecimalField(max_digits=10, decimal_places=8)
    dm = models.FloatField()
    rm = models.FloatField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()


class Filterbankings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    nbit = models.IntegerField()
    npol = models.IntegerField()
    nchan = models.IntegerField()
    tsamp = models.FloatField()
    dm = models.FloatField()


class Foldings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    folding_ephemeris = models.ForeignKey("Ephemerides", models.DO_NOTHING)
    nbin = models.IntegerField()
    npol = models.IntegerField()
    nchan = models.IntegerField()
    dm = models.FloatField(blank=True, null=True)
    tsubint = models.IntegerField()

    @property
    def band(cls):
        freq = cls.processing.observation.instrument_config.frequency
        return get_band(float(freq))


class Instrumentconfigs(models.Model):
    name = models.CharField(max_length=255)
    bandwidth = models.DecimalField(max_digits=12, decimal_places=6)
    frequency = models.DecimalField(max_digits=15, decimal_places=9)
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
    default_embargo = timedelta(days=548)  # 18 months default embargo

    code = models.CharField(max_length=255, unique=True)
    short = models.CharField(max_length=20, default="???")
    embargo_period = models.DurationField(default=default_embargo)
    description = models.CharField(max_length=255, blank=True, null=True)


class Pipelineimages(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    rank = models.IntegerField()
    image_type = models.CharField(max_length=64, blank=True, null=True)
    image = models.CharField(max_length=255)


class Pipelines(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, null=True)
    revision = models.CharField(max_length=16)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    configuration = JSONField(blank=True, null=True)


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
    results = JSONField(blank=True, null=True)


class Pulsaraliases(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    alias = models.CharField(max_length=64)


class Pulsartargets(models.Model):
    target = models.ForeignKey("Targets", models.DO_NOTHING)
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)


class Pulsars(models.Model):
    jname = models.CharField(max_length=64)
    state = models.CharField(max_length=255, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)

    def get_observations_detail_data(cls, get_proposal_filters=get_meertime_filters):
        annotations = {
            "utc": F("processing__observation__utc_start"),
            "bw": F("processing__observation__instrument_config__bandwidth"),
            "length": F("processing__observation__duration"),
            "proposal": F("processing__observation__duration"),
            "beam": F("processing__observation__instrument_config__beam"),
            "nant": F("processing__observation__nant"),
            "nant_eff": F("processing__observation__nant_eff"),
            "results": F("processing__results"),
            "dm_eph": F("folding_ephemeris__dm"),
        }
        folds = Foldings.objects.filter(folding_ephemeris__pulsar=cls).annotate(**annotations)
        return folds


class Rfis(models.Model):
    processing = models.ForeignKey(Processings, models.DO_NOTHING)
    folding = models.ForeignKey(Foldings, models.DO_NOTHING)
    percent_zapped = models.FloatField()


class Targets(models.Model):
    name = models.CharField(max_length=64)
    raj = models.CharField(max_length=16)
    decj = models.CharField(max_length=16)


class Telescopes(models.Model):
    name = models.CharField(max_length=64)


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
    site = models.IntegerField(blank=True, null=True)
    uncertainty = models.FloatField(blank=True, null=True)
    quality = models.IntegerField(blank=True, null=True, choices=QUALITY_CHOICES)
    comment = models.CharField(max_length=255, blank=True, null=True)
