import hashlib
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, OuterRef, Subquery, Max, Min, ExpressionWrapper, Count, Sum, JSONField
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import ugettext_lazy as _
from django_mysql.models import Model
from .logic import get_meertime_filters, get_band
from datetime import timedelta
from .storage import OverwriteStorage, get_upload_location, get_pipeline_upload_location


DATA_QUALITY_CHOICES = [
    ("unassessed", "unassessed"),
    ("good", "good"),
    ("bad", "bad"),
]


class Pulsar(models.Model):
    # TODO would this be better explaied with an ID incase the pulsar name is updated
    jname = models.CharField(max_length=64, unique=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(null=True)

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



class Ephemeris(models.Model):
    limits = {
        "p0": {"max": 10, "deci": 8},
    }
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
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
    ephemeris = JSONField(null=True)
    ephemeris_hash = models.CharField(max_length=32, editable=False, null=True)
    p0 = models.DecimalField(max_digits=limits["p0"]["max"], decimal_places=limits["p0"]["deci"])
    dm = models.FloatField()
    rm = models.FloatField()
    comment = models.TextField(null=True)
    valid_from = models.DateTimeField()
    # we should be making sure valid_to is later than valid_from
    valid_to = models.DateTimeField()

    class Meta:
        unique_together = [["pulsar", "ephemeris_hash", "dm", "rm"]]

    def clean(self, *args, **kwargs):
        # checking valid_to is later than valid_from
        if self.valid_from >= self.valid_to:
            raise ValidationError(_("valid_to must be later than valid_from"))

    def save(self, *args, **kwargs):
        Ephemeris.clean(self)
        self.ephemeris_hash = hashlib.md5(
            json.dumps(self.ephemeris, sort_keys=True, indent=2).encode("utf-8")
        ).hexdigest()
        super(Ephemeris, self).save(*args, **kwargs)


class Template(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    frequency = models.FloatField()
    bandwidth = models.FloatField()
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    location = models.CharField(max_length=255)
    method = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(null=True)



class Calibration(models.Model):
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



class Filterbankings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    nbit = models.IntegerField()
    npol = models.IntegerField()
    nchan = models.IntegerField()
    tsamp = models.FloatField()
    dm = models.FloatField()



class InstrumentConfig(models.Model):
    limits = {"bandwidth": {"max": 12, "deci": 6}, "frequency": {"max": 15, "deci": 9}}
    name = models.CharField(max_length=255)
    bandwidth = models.DecimalField(max_digits=limits["bandwidth"]["max"], decimal_places=limits["bandwidth"]["deci"])
    frequency = models.DecimalField(max_digits=limits["frequency"]["max"], decimal_places=limits["frequency"]["deci"])
    nchan = models.IntegerField()
    npol = models.IntegerField()
    beam = models.CharField(max_length=16)



class Telescope(models.Model):
    name = models.CharField(max_length=64, unique=True)

# TODO is the a difference between program and project?
class Programs(Model):
    telescope = models.ForeignKey(Telescope, models.DO_NOTHING)
    name = models.CharField(max_length=64)


class Project(models.Model):
    program = models.ForeignKey(Programs, models.DO_NOTHING, null=True)
    code = models.CharField(max_length=255, unique=True)
    short = models.CharField(max_length=20, default="???")
    embargo_period = models.DurationField(default=timedelta(days=548)) # default 18 months default embargo
    description = models.CharField(max_length=255, blank=True, null=True)


# TODO Maybe just add this to observations
class Target(models.Model):
    name = models.CharField(max_length=64)
    raj = models.CharField(max_length=16)
    decj = models.CharField(max_length=16)

    class Meta:
        constraints = [UniqueConstraint(fields=["name", "raj", "decj"], name="unique target")]


class Observation(models.Model):
    # TODO Make target either a pulsar or a name
    target = models.ForeignKey(Target, models.DO_NOTHING)
    calibration = models.ForeignKey(Calibration, models.DO_NOTHING, null=True)
    telescope = models.ForeignKey(Telescope, models.DO_NOTHING)
    instrument_config = models.ForeignKey(InstrumentConfig, models.DO_NOTHING)
    project = models.ForeignKey(Project, models.DO_NOTHING)

    utc_start = models.DateTimeField()
    TYPE_CHOICES = [
        ("fold", "fold"),
        ("search", "search"),
    ]
    type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    BAND_CHOICES = [
        ("UHF", "UHF"),
        ("LBAND", "LBAND"),
        ("SBAND_0", "SBAND_0"),
        ("SBAND_1", "SBAND_1"),
        ("SBAND_2", "SBAND_2"),
        ("SBAND_3", "SBAND_3"),
        ("SBAND_4", "SBAND_4"),
    ]
    band = models.CharField(max_length=7, choices=BAND_CHOICES)
    beam = models.IntegerField()
    bandwidth = models.DecimalField(max_digits=12, decimal_places=2)
    config = JSONField(blank=True, null=True)
    duration = models.FloatField(null=True)
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)
    npol = models.IntegerField()
    nbit = models.IntegerField()
    tsamp = models.FloatField()
    nchan = models.IntegerField()
    suspect = models.BooleanField(default=False)
    comment = models.TextField(null=True)

    # Backend folding values
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING)
    fold_nbin = models.IntegerField()
    fold_nchan = models.IntegerField()
    fold_nsub = models.IntegerField()


class PipelineRun(Model):
    """
    Details about the software and pipeline run to process data
    """
    observation = models.ForeignKey(Observation, models.DO_NOTHING)
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING, null=True)
    template = models.ForeignKey(Template, models.DO_NOTHING)

    pipeline_name = models.CharField(max_length=64)
    pipeline_description = models.CharField(max_length=255, blank=True, null=True)
    pipeline_version = models.CharField(max_length=16)
    pipeline_commit = models.CharField(max_length=16)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    job_state = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255)
    configuration = JSONField(blank=True, null=True)


class Pipelineimages(models.Model):
    pipeline_run = models.ForeignKey(PipelineRun, models.DO_NOTHING)
    image = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    image_type = models.CharField(max_length=64, blank=True, null=True)
    cleaned = models.BooleanField(default=True)
    RESOLUTION_CHOICES = [
        ("high", "high"),
        ("low",  "low"),
    ]
    resolution = models.CharField(max_length=4, choices=RESOLUTION_CHOICES)

    class Meta:
        constraints = [
            # TODO this may no longer be necessary with pipeline run
            UniqueConstraint(fields=["processing", "image_type"], name="unique image type for a processing")
        ]


class Pipelinefiles(models.Model):
    pipeline_run = models.ForeignKey(PipelineRun, models.DO_NOTHING)
    file = models.FileField(null=True, upload_to=get_pipeline_upload_location, storage=OverwriteStorage())
    file_type = models.CharField(max_length=32, blank=True, null=True)



# TODO see if pulsartargets can be removed
class Pulsartarget(models.Model):
    target = models.ForeignKey(Target, models.DO_NOTHING)
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)


# TODO I don't understand sessions
class Session(models.Model):
    telescope = models.ForeignKey(Telescope, models.DO_NOTHING)
    start = models.DateTimeField()
    end = models.DateTimeField()

    @classmethod
    def get_last_session(cls):
        return cls.objects.order_by("end").last()

    @classmethod
    def get_session(cls, utc):
        try:
            return cls.objects.get(start__lte=utc, end__gte=utc)
        except Session.DoesNotExist:
            return None



class FoldPulsarResult(models.Model):
    pulsar = models.ForeignKey(Pulsar, on_delete=models.CASCADE)
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    ephemeris = JSONField(null=True)

    embargo_end_date = models.DateTimeField(null=True)
    proposal = models.CharField(max_length=40)
    dm = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    sn = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    flux = models.DecimalField(max_digits=12, decimal_places=6, null=True)
    rm = models.DecimalField(max_digits=12, decimal_places=6, null=True)
    ephemeris_download_link = models.URLField(null=True)
    toas_download_link = models.URLField(null=True)
    percent_rfi_zapped = models.FloatField()



class Toa(models.Model):

    pipeline_run = models.ForeignKey(PipelineRun, models.DO_NOTHING)
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING, null=True)
    template = models.ForeignKey(Template, models.DO_NOTHING)

    mjd = models.CharField(max_length=32, blank=True, null=True)
    uncertainty = models.FloatField(blank=True, null=True)
    frequency = models.FloatField()
    sn = models.FloatField()
    nchan = models.IntegerField()
    nsub = models.IntegerField()
    site = models.CharField(max_length=1, blank=True, null=True)
    quality = models.CharField(max_length=7, blank=True, null=True, choices=DATA_QUALITY_CHOICES)
    flags = JSONField()
