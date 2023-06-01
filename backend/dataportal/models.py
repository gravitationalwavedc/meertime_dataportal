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
    """
    Pulsar is used as a target for the observations so this can also be globular clusters
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    comment = models.TextField(null=True, help_text="Auto generated description based on information from the ANTF catalogue")


class Ephemeris(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    ephemeris = JSONField(unique=True) #TODO Test that json unique works as we expect
    p0 = models.FloatField()
    dm = models.FloatField()
    comment = models.TextField(null=True)
    valid_from = models.DateTimeField()
    # we should be making sure valid_to is later than valid_from
    valid_to = models.DateTimeField()

    def clean(self, *args, **kwargs):
        # checking valid_to is later than valid_from
        if self.valid_from >= self.valid_to:
            raise ValidationError(_("valid_to must be later than valid_from"))

    # def save(self, *args, **kwargs):
    #     Ephemeris.clean(self)
    #     self.ephemeris_hash = hashlib.md5(
    #         json.dumps(self.ephemeris, sort_keys=True, indent=2).encode("utf-8")
    #     ).hexdigest()
    #     super(Ephemeris, self).save(*args, **kwargs)


class Template(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    frequency = models.FloatField()
    bandwidth = models.FloatField()
    nchan = models.IntegerField()
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    location = models.CharField(max_length=255)
    method = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(null=True)
    # TODO upload the file



class Calibration(models.Model):
    # TODO use DELAYCAL_ID to note which calibrator was used.
    CALIBRATION_TYPES = [
        ("pre", "pre"),
        ("post", "post"),
        ("none", "none"),
    ]
    calibration_type = models.CharField(max_length=4, choices=CALIBRATION_TYPES)
    location = models.CharField(max_length=255, blank=True, null=True)


class Telescope(models.Model):
    name = models.CharField(max_length=64, unique=True)

# TODO is the a difference between program and project?
class MainProject(Model):
    """
    E.g. Meertime and trapam
    """
    telescope = models.ForeignKey(Telescope, models.DO_NOTHING)
    name = models.CharField(max_length=64)


class Project(models.Model):
    """
    E.g. thousand pulsar array, RelBin
    """
    program = models.ForeignKey(MainProject, models.DO_NOTHING, null=True)
    code = models.CharField(max_length=255, unique=True)
    short = models.CharField(max_length=20, default="???")
    embargo_period = models.DurationField(default=timedelta(days=548)) # default 18 months default embargo
    description = models.CharField(max_length=255, blank=True, null=True)


class Session(models.Model):
    """
    Sessions are observing runs that are phased up with the same calibrator.
    They can be used to infer if there is something wrong with the telescope
    if all observations of that session are unusable.
    Within two hours and have the same calibration for Meerkat
    """
    calibration = models.ForeignKey(Calibration, models.DO_NOTHING, null=True)
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


class Observation(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    telescope = models.ForeignKey(Telescope, models.DO_NOTHING)
    project = models.ForeignKey(Project, models.DO_NOTHING)
    session = models.ForeignKey(Session, models.DO_NOTHING, null=True)

    # Frequency fields
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
    frequency = models.FloatField()
    bandwidth = models.FloatField()
    nchan = models.IntegerField()

    # Antenna
    beam = models.IntegerField()
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)
    npol = models.IntegerField()

    TYPE_CHOICES = [
        ("fold", "fold"),
        ("search", "search"),
        # TODO may want to do baseband obs
    ]
    type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    utc_start = models.DateTimeField()
    raj = models.CharField(max_length=16)
    decj = models.CharField(max_length=16)
    duration = models.FloatField(null=True)
    nbit = models.IntegerField()
    tsamp = models.FloatField()

    # Backend folding values
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING, blank=True, null=True)
    fold_nbin = models.IntegerField(blank=True, null=True)
    fold_nchan = models.IntegerField(blank=True, null=True)
    fold_nsub = models.IntegerField(blank=True, null=True)

    # Backend search values
    filterbank_nbit = models.IntegerField(blank=True, null=True)
    filterbank_npol = models.IntegerField(blank=True, null=True)
    filterbank_nchan = models.IntegerField(blank=True, null=True)
    filterbank_tsamp = models.FloatField(blank=True, null=True)
    filterbank_dm = models.FloatField(blank=True, null=True)


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
    # TODO data size estimation


class PipelineImage(models.Model):
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


class PipelineFile(models.Model):
    pipeline_run = models.ForeignKey(PipelineRun, models.DO_NOTHING)
    file = models.FileField(null=True, upload_to=get_pipeline_upload_location, storage=OverwriteStorage())
    file_type = models.CharField(max_length=32, blank=True, null=True)



class FoldPulsarResult(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)

    ephemeris = JSONField(null=True)
    embargo_end_date = models.DateTimeField(null=True)
    proposal = models.CharField(max_length=40)
    dm = models.FloatField(null=True)
    sn = models.FloatField(null=True)
    flux = models.FloatField(null=True)
    rm = models.FloatField(null=True)
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
    quality = models.CharField(max_length=10, blank=True, null=True, choices=DATA_QUALITY_CHOICES)
    flags = JSONField()
