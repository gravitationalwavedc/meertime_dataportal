import math
import hashlib
import json
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import ugettext_lazy as _
from django_mysql.models import Model
from .logic import get_meertime_filters, get_band
from datetime import timedelta
from .storage import OverwriteStorage, get_upload_location, get_pipeline_upload_location, get_template_upload_location, create_file_hash

from user_manage.models import User
from utils.observing_bands import get_band


DATA_QUALITY_CHOICES = [
    ("unassessed", "unassessed"),
    ("good", "good"),
    ("bad", "bad"),
]

BAND_CHOICES = [
    ("UHF", "UHF"),
    ("LBAND", "LBAND"),
    ("SBAND_0", "SBAND_0"),
    ("SBAND_1", "SBAND_1"),
    ("SBAND_2", "SBAND_2"),
    ("SBAND_3", "SBAND_3"),
    ("SBAND_4", "SBAND_4"),
]

class Pulsar(models.Model):
    """
    Pulsar is used as a target for the observations so this can also be globular clusters
    """
    name = models.CharField(max_length=32, unique=True)
    comment = models.TextField(null=True, help_text="Auto generated description based on information from the ANTF catalogue")

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_query(cls, **kwargs):
        return cls.objects.filter(**kwargs)


class Telescope(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.name}"


class MainProject(Model):
    """
    E.g. Meertime and trapam
    """
    telescope = models.ForeignKey(Telescope, models.DO_NOTHING)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Project(models.Model):
    """
    E.g. thousand pulsar array, RelBin
    """
    main_project = models.ForeignKey(MainProject, models.DO_NOTHING, null=True)
    code = models.CharField(max_length=255, unique=True)
    short = models.CharField(max_length=20, default="???")
    embargo_period = models.DurationField(default=timedelta(days=548)) # default 18 months default embargo
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.code}"

    @classmethod
    def get_query(cls, **kwargs):
        if "code" in kwargs:
            if kwargs["code"] == "All":
                kwargs.pop("code")
            else:
                kwargs["code"] = kwargs.pop("code")
        return cls.objects.filter(**kwargs)


class Ephemeris(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    project = models.ForeignKey(Project, models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ephemeris_data = models.JSONField(null=True)
    ephemeris_hash = models.CharField(max_length=32, editable=False, null=True)
    p0 = models.FloatField()
    dm = models.FloatField()
    valid_from = models.DateTimeField(default=datetime.fromtimestamp(0))
    valid_to   = models.DateTimeField(default=datetime.fromtimestamp(4294967295))
    comment = models.TextField(null=True)

    def clean(self, *args, **kwargs):
        # checking valid_to is later than valid_from
        if self.valid_from >= self.valid_to:
            raise ValidationError(_("valid_to must be later than valid_from"))

    def save(self, *args, **kwargs):
        Ephemeris.clean(self)
        self.ephemeris_hash = hashlib.md5(
            json.dumps(self.ephemeris_data, sort_keys=True, indent=2).encode("utf-8")
        ).hexdigest()
        super(Ephemeris, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    "project",
                    "ephemeris_hash",
                ],
                name="Unique ephemeris for each project"
            )
        ]


class Template(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    project = models.ForeignKey(Project, models.DO_NOTHING)
    template_file = models.FileField(upload_to=get_template_upload_location, storage=OverwriteStorage(), null=True)
    template_hash = models.CharField(max_length=64, editable=False, null=True)

    band = models.CharField(max_length=7, choices=BAND_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        Template.clean(self)
        if self.template_file:
            # This may be redundant as the rest api already caculates the hash
            self.template_hash = create_file_hash(self.template_file)
        super(Template, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    "pulsar",
                    "project",
                    "band",
                    "template_hash",
                ],
                name="Unique template for each pulsar, project and band."
            )
        ]


class Calibration(models.Model):
    # TODO use DELAYCAL_ID to note which calibrator was used.
    CALIBRATION_TYPES = [
        ("pre", "pre"),
        ("post", "post"),
        ("none", "none"),
    ]
    delay_cal_id = models.CharField(max_length=16, blank=True, null=True)
    phase_up_id = models.CharField(max_length=16, blank=True, null=True)
    calibration_type = models.CharField(max_length=4, choices=CALIBRATION_TYPES)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.id}_{self.delay_cal_id}"


class Observation(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    telescope = models.ForeignKey(Telescope, models.DO_NOTHING)
    project = models.ForeignKey(Project, models.DO_NOTHING)
    calibration = models.ForeignKey(Calibration, models.DO_NOTHING, null=True)

    # Frequency fields
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
        ("cal", "cal"),
        ("fold", "fold"),
        ("search", "search"),
        # TODO may want to do baseband obs
    ]
    obs_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    utc_start = models.DateTimeField()
    raj  = models.CharField(max_length=32)
    decj = models.CharField(max_length=32)
    duration = models.FloatField(null=True)
    nbit = models.IntegerField()
    tsamp = models.FloatField()

    # Backend folding values
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING, to_field="id", blank=True, null=True)
    fold_nbin = models.IntegerField(blank=True, null=True)
    fold_nchan = models.IntegerField(blank=True, null=True)
    fold_tsubint = models.IntegerField(blank=True, null=True)

    # Backend search values
    filterbank_nbit = models.IntegerField(blank=True, null=True)
    filterbank_npol = models.IntegerField(blank=True, null=True)
    filterbank_nchan = models.IntegerField(blank=True, null=True)
    filterbank_tsamp = models.FloatField(blank=True, null=True)
    filterbank_dm = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        Observation.clean(self)
        self.band = get_band(self.frequency, self.bandwidth)
        super(Observation, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.utc_start} {self.beam}"

    @classmethod
    def get_query(cls, **kwargs):
        if "first" in kwargs:
            kwargs.pop("first")
        if "last" in kwargs:
            kwargs.pop("last")
        if "before" in kwargs:
            kwargs.pop("before")
        if "after" in kwargs:
            kwargs.pop("after")
        return cls.objects.filter(**kwargs)


class PipelineRun(Model):
    """
    Details about the software and pipeline run to process data
    """
    observation = models.ForeignKey(Observation, models.DO_NOTHING)
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING, to_field="id", null=True)
    template = models.ForeignKey(Template, models.DO_NOTHING)

    pipeline_name = models.CharField(max_length=64)
    pipeline_description = models.CharField(max_length=255, blank=True, null=True)
    pipeline_version = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=64)
    JOB_STATE_CHOICES = [
        ("Pending",   "Pending"),
        ("Running",   "Running"),
        ("Completed", "Completed"),
        ("Failed",    "Failed"),
        ("Cancelled", "Cancelled"),
    ]
    job_state = models.CharField(max_length=9, choices=JOB_STATE_CHOICES, default="Pending")
    location = models.CharField(max_length=255)
    configuration = models.JSONField(blank=True, null=True)

    ephemeris_download_link = models.URLField(null=True)
    toas_download_link = models.URLField(null=True)

    # DM results
    dm       = models.FloatField(null=True)
    dm_err   = models.FloatField(null=True)
    dm_epoch = models.FloatField(null=True)
    dm_chi2r = models.FloatField(null=True)
    dm_tres  = models.FloatField(null=True)

    # Other results
    sn = models.FloatField(null=True)
    flux = models.FloatField(null=True)
    rm = models.FloatField(null=True)
    percent_rfi_zapped = models.FloatField(null=True)


class FoldPulsarResult(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE)
    pipeline_run = models.ForeignKey(PipelineRun, on_delete=models.CASCADE)
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)

    embargo_end_date = models.DateTimeField(null=True)
    @classmethod
    def get_query(cls, **kwargs):
        return cls.objects.filter(**kwargs)


class PulsarFoldSummary(models.Model):
    """
    Summary of all observations of a pulsar
    """
    pulsar = models.ForeignKey(Pulsar, models.DO_NOTHING)
    main_project = models.ForeignKey(MainProject, models.DO_NOTHING)

    # Obs summary
    first_observation = models.DateTimeField()
    latest_observation = models.DateTimeField()
    timespan = models.IntegerField()
    number_of_observations = models.IntegerField()
    total_integration_hours = models.FloatField()
    last_integration_minutes = models.FloatField(null=True)
    all_bands = models.CharField(max_length=500)

    # Results summary
    last_sn = models.FloatField()
    highest_sn = models.FloatField()
    lowest_sn = models.FloatField()
    avg_sn_pipe = models.FloatField(null=True)
    max_sn_pipe = models.FloatField(null=True)

    # Project summary
    most_common_project = models.CharField(max_length=64) # Tis could be a foreign key
    all_projects = models.CharField(max_length=500)

    class Meta:
        unique_together = [["main_project", "pulsar"]]
        ordering = ["-latest_observation"]

    @classmethod
    def get_query(cls, **kwargs):
        if "band" in kwargs:
            if kwargs["band"] == "All":
                kwargs.pop("band")
            else:
                kwargs["all_bands__icontains"] = kwargs.pop("band")

        if "most_common_project" in kwargs:
            if kwargs["most_common_project"] == "All":
                kwargs.pop("most_common_project")
            else:
                kwargs["most_common_project__icontains"] = kwargs.pop("most_common_project")

        if "main_project" in kwargs and kwargs["main_project"] == "All":
            kwargs.pop("main_project")
        elif "main_project" in kwargs:
            kwargs["main_project__name"] = kwargs.pop("main_project")

        return cls.objects.filter(**kwargs)

    @classmethod
    def get_most_common_project(cls, observations):
        project_counts = {}
        for observation in observations:
            # If you like it, then you should have put a key on it.
            project_short = observation.project.short
            if project_short in project_counts:
                # I'm a survivor, I'm not a quitter, I'm gonna increment until I'm a winner.
                project_counts[project_short] += 1
            else:
                project_counts[project_short] = 1

        # To the left, to the left
        # Find the key with the highest count, to the left
        return max(project_counts, key=project_counts.get)

    @classmethod
    def update_or_create(cls, pulsar, main_project):
        """
        Every time a PipelineRun is saved, we want to update the PulsarFoldSummary
        model so it accurately summaries all fold observations for that pulsar.

        Parameters:
            pulsar: A pulsar model instance.
        """
        # Get all the fold observations for that pulsar
        observations = Observation.objects.filter(pulsar=pulsar, obs_type="fold").order_by("utc_start")

        # Process observation summary
        first_observation  = observations.first()
        latest_observation = observations.last()
        timespan = (latest_observation.utc_start - first_observation.utc_start).days + 1
        number_of_observations = observations.count()
        total_integration_hours = sum(observation.duration for observation in observations) / 3600
        last_integration_minutes = latest_observation.duration / 60
        all_bands = ", ".join(
            {observation.band for observation in observations}
        )

        # Process results summary
        results = FoldPulsarResult.objects.filter(pulsar=pulsar).order_by("observation__utc_start")
        last_sn = results.last().pipeline_run.sn
        sn_list = [result.pipeline_run.sn or 0 for result in results]
        highest_sn = max(sn_list)
        lowest_sn  = min(sn_list)
        # Since SNR is proportional to the sqrt of the observation length
        # we can normalise the SNR to an equivalent 5 minute observation
        sn_5min_list = []
        for result in results:
            if result.pipeline_run.sn is not None:
                sn_5min_list.append(result.pipeline_run.sn / math.sqrt(result.observation.duration) * math.sqrt(300) )
        if len(sn_5min_list) > 0:
            avg_sn_pipe = sum(sn_5min_list) / len(sn_5min_list)
            max_sn_pipe = max(sn_5min_list)
        else:
            avg_sn_pipe = 0
            max_sn_pipe = 0

        # Process project summary
        all_projects = ", ".join(
            {observation.project.short for observation in observations}
        )
        most_common_project = cls.get_most_common_project(observations)

        new_pulsar_fold_summary, created = PulsarFoldSummary.objects.update_or_create(
            pulsar=pulsar,
            main_project=main_project,
            defaults={
                "first_observation": first_observation.utc_start,
                "latest_observation": latest_observation.utc_start,
                "timespan": timespan,
                "number_of_observations": number_of_observations,
                "total_integration_hours": total_integration_hours,
                "last_integration_minutes": last_integration_minutes,
                "all_bands": all_bands,
                "last_sn": last_sn or 0,
                "highest_sn": highest_sn or 0,
                "lowest_sn": lowest_sn or 0,
                "avg_sn_pipe": avg_sn_pipe,
                "max_sn_pipe": max_sn_pipe,
                "all_projects": all_projects,
                "most_common_project": most_common_project,
            },
        )
        return new_pulsar_fold_summary, created


class PipelineImage(models.Model):
    fold_pulsar_result = models.ForeignKey(FoldPulsarResult, models.DO_NOTHING, related_name="images",)
    image = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    url = models.URLField(null=True)
    cleaned = models.BooleanField(default=True)
    IMAGE_TYPE_CHOICES = [
        ("toa-single",  "toa-single"),
        ("profile",     "profile"),
        ("profile-pol", "profile-pol"),
        ("phase-time",  "phase-time"),
        ("phase-freq",  "phase-freq"),
        ("bandpass",    "bandpass"),
        ("snr-cumul",   "snr-cumul"),
        ("snr-single",  "snr-single"),
    ]
    image_type = models.CharField(max_length=16, choices=IMAGE_TYPE_CHOICES)
    RESOLUTION_CHOICES = [
        ("high", "high"),
        ("low",  "low"),
    ]
    resolution = models.CharField(max_length=4, choices=RESOLUTION_CHOICES)

    class Meta:
        constraints = [
            # TODO this may no longer be necessary with pipeline run
            UniqueConstraint(
                fields=[
                    "fold_pulsar_result",
                    "image_type",
                    "cleaned",
                    "resolution",
                ],
                name="Unique image type for a FoldPulsarResult"
            )
        ]

    def save(self, *args, **kwargs):
        PipelineImage.clean(self)
        self.url = self.image.url
        super(PipelineImage, self).save(*args, **kwargs)


class PipelineFile(models.Model):
    pipeline_run = models.ForeignKey(PipelineRun, models.DO_NOTHING)
    file = models.FileField(null=True, upload_to=get_pipeline_upload_location, storage=OverwriteStorage())
    # TODO make it check this path in the get or create so we're not making redundant files
    ozstar_path = models.CharField(max_length=256, blank=True, null=True)
    file_type = models.CharField(max_length=32, blank=True, null=True)
    # TODO data size estimation


class Toa(models.Model):
    # foreign keys
    pipeline_run = models.ForeignKey(PipelineRun, models.DO_NOTHING)
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING, to_field="id")
    template = models.ForeignKey(Template, models.DO_NOTHING)

    # toa results
    archive   = models.CharField(max_length=128)
    freq_MHz  = models.FloatField()
    mjd       = models.DecimalField(decimal_places=12, max_digits=18)
    mjd_err   = models.FloatField()
    telescope = models.CharField(max_length=32)

    # The flags from the toa file
    fe     = models.CharField(max_length=32, null=True)
    be     = models.CharField(max_length=32, null=True)
    f      = models.CharField(max_length=32, null=True)
    bw     = models.IntegerField(null=True)
    tobs   = models.IntegerField(null=True)
    tmplt  = models.CharField(max_length=64, null=True)
    gof    = models.FloatField(null=True)
    nbin   = models.IntegerField(null=True)
    nch    = models.IntegerField(null=True)
    chan   = models.IntegerField(null=True)
    rcvr   = models.CharField(max_length=32, null=True)
    snr    = models.FloatField(null=True)
    length = models.IntegerField(null=True)
    subint = models.IntegerField(null=True)


class Residual(models.Model):
    pipeline_run = models.ForeignKey(PipelineRun, models.DO_NOTHING)
    ephemeris = models.ForeignKey(Ephemeris, models.DO_NOTHING, to_field="id", null=True)
    template = models.ForeignKey(Template, models.DO_NOTHING)

    # X axis types
    mjd = models.FloatField()
    day_of_year = models.FloatField()
    binary_orbital_phase = models.FloatField()

    # Y axis types
    residual_sec     = models.FloatField()
    residual_sec_err = models.FloatField()
    residual_phase     = models.FloatField() # pulse period phase
    residual_phase_err = models.FloatField()

    sn = models.FloatField()
    frequency = models.FloatField()
    nchan = models.IntegerField()
    nsub = models.IntegerField()

    site = models.CharField(max_length=1, blank=True, null=True)
    quality = models.CharField(max_length=10, blank=True, null=True, choices=DATA_QUALITY_CHOICES)
    flags = models.JSONField()
