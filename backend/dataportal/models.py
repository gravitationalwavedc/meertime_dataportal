import math
import json
import pytz
import hashlib
from datetime import datetime, timedelta

import numpy as np
from astropy.time import Time

from graphql import GraphQLError
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.db.models.constraints import UniqueConstraint
from django.db.models import Model, F, Sum

from .storage import OverwriteStorage, get_upload_location, get_template_upload_location, create_file_hash
from user_manage.models import User
from utils.observing_bands import get_band
from utils.binary_phase import get_binary_phase, is_binary
from utils.constants import UserRole
from utils.toa import toa_line_to_dict, toa_dict_to_line
from utils.ephemeris import parse_ephemeris_file


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
    ("OTHER", "OTHER"),
    ("UHF_NS", "UHF_NS"), # For Molonglo NS arm
]

OBS_TYPE_CHOICES = [
    ("cal", "cal"),
    ("fold", "fold"),
    ("search", "search"),
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
    telescope = models.ForeignKey(Telescope, models.CASCADE)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Project(models.Model):
    """
    E.g. thousand pulsar array, RelBin
    """
    main_project = models.ForeignKey(MainProject, models.CASCADE, null=True)
    code = models.CharField(max_length=255, unique=True)
    short = models.CharField(max_length=20, default="???")
    embargo_period = models.DurationField(default=timedelta(days=548)) # default 18 months default embargo
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.code}_{self.short}"

    @classmethod
    def get_query(cls, **kwargs):
        if "code" in kwargs:
            if kwargs["code"] == "All":
                kwargs.pop("code")
            else:
                kwargs["code"] = kwargs.pop("code")
        return cls.objects.filter(**kwargs)


class Ephemeris(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.CASCADE)
    project = models.ForeignKey(Project, models.CASCADE)
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
    pulsar = models.ForeignKey(Pulsar, models.CASCADE)
    project = models.ForeignKey(Project, models.CASCADE)
    template_file = models.FileField(upload_to=get_template_upload_location, storage=OverwriteStorage(), null=True)
    template_hash = models.CharField(max_length=64, null=True)

    band = models.CharField(max_length=7, choices=BAND_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

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
    schedule_block_id = models.CharField(max_length=16, blank=True, null=True)
    calibration_type = models.CharField(max_length=4, choices=CALIBRATION_TYPES)
    location = models.CharField(max_length=255, blank=True, null=True)

    # The following will be populated by the observations
    start = models.DateTimeField(null=True)
    end   = models.DateTimeField(null=True)
    all_projects = models.CharField(max_length=255, blank=True, null=True)
    n_observations = models.IntegerField(null=True)
    n_ant_min = models.IntegerField(null=True)
    n_ant_max = models.IntegerField(null=True)
    total_integration_time_seconds = models.FloatField(null=True)

    @classmethod
    def update_observation_session(cls, calibration):
        """
        Every time a Observation is saved, we want to update the Calibration
        model so it accurately summaries all observations for that Calibration (session).

        Parameters:
            calibration: Calibration django model
                A Calibration model instance.
        """
        # Grab observations for the calibrator
        observations = Observation.objects.filter(calibration=calibration)

        start = observations.order_by('utc_start').first().utc_start
        end = observations.order_by('utc_start').last().utc_start
        all_projects = ", ".join(
            {observation.project.short for observation in observations.all()}
        )
        n_observations = observations.count()
        n_ant_min = observations.order_by('nant').first().nant
        n_ant_max = observations.order_by('nant').last().nant
        total_integration_time_seconds = sum(observations.all().values_list('duration', flat=True))

        # Update the calibration values
        calibration.start = start
        calibration.end = end
        calibration.all_projects = all_projects
        calibration.n_observations = n_observations
        calibration.n_ant_min = n_ant_min
        calibration.n_ant_max = n_ant_max
        calibration.total_integration_time_seconds = total_integration_time_seconds
        calibration.save()

        return calibration


    def __str__(self):
        return f"{self.id}_{self.schedule_block_id}"

    class Meta:
        ordering = ["-start"]


class Observation(models.Model):
    pulsar = models.ForeignKey(Pulsar, models.CASCADE)
    telescope = models.ForeignKey(Telescope, models.CASCADE)
    project = models.ForeignKey(Project, models.CASCADE)
    calibration = models.ForeignKey(Calibration, models.SET_NULL, null=True, related_name="observations")

    embargo_end_date = models.DateTimeField(null=True)

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
    obs_type = models.CharField(max_length=6, choices=OBS_TYPE_CHOICES)
    utc_start = models.DateTimeField()
    day_of_year = models.FloatField(null=True)
    binary_orbital_phase = models.FloatField(null=True)
    raj  = models.CharField(max_length=32)
    decj = models.CharField(max_length=32)
    duration = models.FloatField(null=True)
    nbit = models.IntegerField()
    tsamp = models.FloatField()

    # Backend folding values
    ephemeris = models.ForeignKey(Ephemeris, models.SET_NULL, to_field="id", blank=True, null=True)
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
        if self.project.main_project.name == "MONSPSR":
            # All observations with Molonglo are currently UHF band with the NS arm
            self.band = "UHF_NS"
        else:
            self.band = get_band(self.frequency, self.bandwidth)
        self.day_of_year = self.utc_start.timetuple().tm_yday \
            + self.utc_start.hour / 24.0 \
            + self.utc_start.minute / (24.0 * 60.0) \
            + self.utc_start.second / (24.0 * 60.0 * 60.0)
        if self.ephemeris is not None:
            ephemeris_dict = json.loads(self.ephemeris.ephemeris_data)
            if is_binary(ephemeris_dict):
                centre_obs_mjd = self.utc_start + timedelta(seconds=self.duration/2)
                self.binary_orbital_phase = get_binary_phase(np.array([Time(centre_obs_mjd).mjd]), ephemeris_dict)
        self.embargo_end_date = self.utc_start + self.project.embargo_period
        super(Observation, self).save(*args, **kwargs)

    def is_restricted(self, user):
        # If the user role isn't restricted they can access everything
        if user.role.upper() in [UserRole.UNRESTRICTED.value, UserRole.ADMIN.value]:
            return False

        # If there's no embargo then it's not restricted
        return self.embargo_end_date >= datetime.now(tz=pytz.UTC)

    def __str__(self):
        return f"{self.utc_start} {self.beam}"


class ObservationSummary(Model):
    # Foreign Keys that can be none when they're summarising all instead of an individual model
    pulsar = models.ForeignKey(Pulsar, models.CASCADE, null=True)
    main_project = models.ForeignKey(MainProject, models.CASCADE, null=True)
    project = models.ForeignKey(Project, models.CASCADE, null=True)
    calibration = models.ForeignKey(Calibration, models.CASCADE, null=True, related_name="observation_summaries")
    obs_type = models.CharField(max_length=6, choices=OBS_TYPE_CHOICES, null=True)
    band = models.CharField(max_length=7, choices=BAND_CHOICES, null=True)

    # Summary values
    observations = models.IntegerField(blank=True, null=True)
    pulsars = models.IntegerField(blank=True, null=True)
    projects = models.IntegerField(blank=True, null=True)
    estimated_disk_space_gb = models.FloatField(blank=True, null=True)
    observation_hours = models.IntegerField(blank=True, null=True)
    timespan_days = models.IntegerField(blank=True, null=True)
    min_duration = models.FloatField(blank=True, null=True)
    max_duration = models.FloatField(blank=True, null=True)

    @classmethod
    def update_or_create(cls, obs_type, pulsar, main_project, project, calibration, band):
        """
        Every time a Observation is saved, we want to update the ObservationSummary
        model so it accurately summaries all observations for the input filters.

        Parameters:
            obs_type: str
                A Pulsar model instance.
            main_project: MainProject django model
                A MainProject model instance.
        """
        # Create a kwargs for the filter that doesn't use the foreign keys that are none
        kwargs = {}
        if obs_type is not None:
            kwargs["obs_type"] = obs_type
        if pulsar is not None:
            kwargs["pulsar"] = pulsar
        if main_project is not None:
            kwargs["project__main_project"] = main_project
        if project is not None:
            kwargs["project"] = project
        if calibration is not None:
            kwargs["calibration"] = calibration
        if band is not None:
            kwargs["band"] = band
        all_observations = Observation.objects.filter(**kwargs)
        if len(all_observations) == 0:
            # No observations for this combo so do not create a summary
            return None, False

        min_utc = all_observations.order_by("utc_start").first().utc_start
        max_utc = all_observations.order_by("utc_start").last().utc_start

        observations = len(all_observations)
        pulsars = len(all_observations.values_list('pulsar__name', flat=True).distinct())
        projects = len(all_observations.values_list('project', flat=True).distinct())
        observation_hours = all_observations.aggregate(total=Sum('duration'))['total'] / 3600
        min_duration = all_observations.order_by("duration").first().duration
        max_duration = all_observations.order_by("duration").last().duration

        duration = max_utc - min_utc
        # Add 1 day to the end result because the timespan should show the rounded up number of days
        timespan_days = duration.days + 1

        if obs_type == "fold":
            try:
                total_bytes = all_observations.aggregate(total_bytes=Sum(
                    F('duration') / F('fold_tsubint') * F('fold_nbin') * F('fold_nchan') * F('npol') * 2
                ))['total_bytes']
            except ZeroDivisionError:
                total_bytes = 0
        else:
            total_bytes = 0
        estimated_disk_space_gb = total_bytes/ (1024 ** 3)

        # Update oc create the model
        new_observation_summary, created = ObservationSummary.objects.update_or_create(
            pulsar=pulsar,
            main_project=main_project,
            project=project,
            calibration=calibration,
            obs_type=obs_type,
            band=band,
            defaults={
                "observations": observations,
                "pulsars": pulsars,
                "projects": projects,
                "estimated_disk_space_gb": estimated_disk_space_gb,
                "observation_hours": observation_hours,
                "timespan_days": timespan_days,
                "min_duration": min_duration,
                "max_duration": max_duration,
            },
        )
        if not created:
            # If updating a model need to save the new values as defaults will not be used
            new_observation_summary.observations
            new_observation_summary.pulsars
            new_observation_summary.projects
            new_observation_summary.estimated_disk_space_gb
            new_observation_summary.observation_hours
            new_observation_summary.timespan_days
            new_observation_summary.min_duration
            new_observation_summary.max_duration
            new_observation_summary.save()
        return new_observation_summary, created


class PipelineRun(Model):
    """
    Details about the software and pipeline run to process data
    """
    observation = models.ForeignKey(Observation, models.CASCADE, related_name="pipeline_runs")
    ephemeris = models.ForeignKey(Ephemeris, models.SET_NULL, null=True)
    template = models.ForeignKey(Template, models.SET_NULL, null=True)

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
    rm_err = models.FloatField(null=True)
    percent_rfi_zapped = models.FloatField(null=True)


class PulsarFoldResult(models.Model):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE, related_name="pulsar_fold_results")
    pipeline_run = models.ForeignKey(PipelineRun, on_delete=models.CASCADE)
    pulsar = models.ForeignKey(Pulsar, models.CASCADE)



class PulsarFoldSummary(models.Model):
    """
    Summary of all the fold observations of a pulsar
    """
    pulsar = models.ForeignKey(Pulsar, models.CASCADE)
    main_project = models.ForeignKey(MainProject, models.CASCADE)

    # Obs summary
    first_observation = models.DateTimeField()
    latest_observation = models.DateTimeField()
    latest_observation_beam = models.IntegerField()
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

        if "project" in kwargs:
            if kwargs["project"] == "All":
                kwargs.pop("project")
            else:
                kwargs["all_projects__icontains"] = kwargs.pop("project")

        if "main_project" in kwargs and kwargs["main_project"] == "All":
            kwargs.pop("main_project")
        elif "main_project" in kwargs:
            kwargs["main_project__name__icontains"] = kwargs.pop("main_project")

        return cls.objects.select_related("pulsar").filter(**kwargs)

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
            pulsar: Pulsar django model
                A Pulsar model instance.
            main_project: MainProject django model
                A MainProject model instance.
        """
        # Get all the fold observations for that pulsar
        observations = Observation.objects.select_related(
            "pulsar",
            "project"
        ).filter(
            pulsar=pulsar,
            project__main_project=main_project,
            obs_type="fold"
        ).order_by("utc_start")

        # Process observation summary
        first_observation  = observations.first()
        latest_observation = observations.last()
        timespan = (latest_observation.utc_start - first_observation.utc_start).days + 1
        number_of_observations = observations.count()
        total_integration_hours = observations.aggregate(total=Sum('duration'))['total'] / 3600
        last_integration_minutes = latest_observation.duration / 60
        all_bands = ", ".join(list(set(observations.values_list('band', flat=True))))

        # Process results summary
        results = PulsarFoldResult.objects.select_related("pulsar", "pipeline_run", "observation").filter(pulsar=pulsar).order_by("observation__utc_start")
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
        all_projects = ", ".join(list(set(observations.values_list('project__short', flat=True))))
        most_common_project = cls.get_most_common_project(observations)

        new_pulsar_fold_summary, created = PulsarFoldSummary.objects.update_or_create(
            pulsar=pulsar,
            main_project=main_project,
            defaults={
                "first_observation": first_observation.utc_start,
                "latest_observation": latest_observation.utc_start,
                "latest_observation_beam": latest_observation.beam,
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
        if not created:
            # If updating a model need to save the new values as defaults will not be used
            new_pulsar_fold_summary.first_observation
            new_pulsar_fold_summary.latest_observation
            new_pulsar_fold_summary.latest_observation_beam
            new_pulsar_fold_summary.timespan
            new_pulsar_fold_summary.number_of_observations
            new_pulsar_fold_summary.total_integration_hours
            new_pulsar_fold_summary.last_integration_minutes
            new_pulsar_fold_summary.all_bands
            new_pulsar_fold_summary.all_projects
            new_pulsar_fold_summary.most_common_project
            new_pulsar_fold_summary.save()
        return new_pulsar_fold_summary, created


class PulsarSearchSummary(models.Model):
    """
    Summary of all the search observations of a pulsar
    """
    pulsar = models.ForeignKey(Pulsar, models.CASCADE)
    main_project = models.ForeignKey(MainProject, models.CASCADE)

    # Obs summary
    first_observation = models.DateTimeField()
    latest_observation = models.DateTimeField()
    timespan = models.IntegerField()
    number_of_observations = models.IntegerField()
    total_integration_hours = models.FloatField()
    last_integration_minutes = models.FloatField(null=True)
    all_bands = models.CharField(max_length=500)

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

        if "project" in kwargs:
            if kwargs["project"] == "All":
                kwargs.pop("project")
            else:
                kwargs["all_projects__icontains"] = kwargs.pop("project")

        if "main_project" in kwargs and kwargs["main_project"] == "All":
            kwargs.pop("main_project")
        elif "main_project" in kwargs:
            kwargs["main_project__name__icontains"] = kwargs.pop("main_project")

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
            pulsar: Pulsar django model
                A Pulsar model instance.
            main_project: MainProject django model
                A MainProject model instance.
        """
        # Get all the fold observations for that pulsar
        observations = Observation.objects.filter(pulsar=pulsar, obs_type="search").order_by("utc_start")

        # Process observation summary
        first_observation  = observations.first()
        latest_observation = observations.last()
        timespan = (latest_observation.utc_start - first_observation.utc_start).days + 1
        number_of_observations = observations.count()
        total_integration_hours = observations.aggregate(total=Sum('duration'))['total'] / 3600
        last_integration_minutes = latest_observation.duration / 60
        all_bands = ", ".join(
            {observation.band for observation in observations}
        )

        # Process project summary
        all_projects = ", ".join(
            {observation.project.short for observation in observations}
        )
        most_common_project = cls.get_most_common_project(observations)

        new_pulsar_search_summary, created = PulsarSearchSummary.objects.update_or_create(
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
                "all_projects": all_projects,
                "most_common_project": most_common_project,
            },
        )
        if not created:
            # If updating a model need to save the new values as defaults will not be used
            new_pulsar_search_summary.first_observation
            new_pulsar_search_summary.latest_observation
            new_pulsar_search_summary.timespan
            new_pulsar_search_summary.number_of_observations
            new_pulsar_search_summary.total_integration_hours
            new_pulsar_search_summary.last_integration_minutes
            new_pulsar_search_summary.all_bands
            new_pulsar_search_summary.all_projects
            new_pulsar_search_summary.most_common_project
            new_pulsar_search_summary.save()
        return new_pulsar_search_summary, created


class PipelineImage(models.Model):
    pulsar_fold_result = models.ForeignKey(PulsarFoldResult, models.CASCADE, related_name="images",)
    image = models.ImageField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    url = models.URLField(null=True)
    cleaned = models.BooleanField(default=True)
    IMAGE_TYPE_CHOICES = [
        ("toa-single", "toa-single"),
        ("profile", "profile"),
        ("profile-pol", "profile-pol"),
        ("phase-time", "phase-time"),
        ("phase-freq", "phase-freq"),
        ("bandpass", "bandpass"),
        ("dynamic-spectrum", "dynamic-spectrum"),
        ("snr-cumul", "snr-cumul"),
        ("snr-single", "snr-single"),
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
                    "pulsar_fold_result",
                    "image_type",
                    "cleaned",
                    "resolution",
                ],
                name="Unique image type for a PulsarFoldResult"
            )
        ]

    def save(self, *args, **kwargs):
        PipelineImage.clean(self)
        if self.image:
            self.url = self.image.url
        super(PipelineImage, self).save(*args, **kwargs)

class PipelineFile(models.Model):
    pulsar_fold_result = models.ForeignKey(PulsarFoldResult, models.CASCADE, related_name="files",)
    file = models.FileField(null=True, upload_to=get_upload_location, storage=OverwriteStorage())
    FILE_TYPE_CHOICES = [
        ("FTS",  "FTS"),
    ]
    file_type = models.CharField(max_length=16, choices=FILE_TYPE_CHOICES)

    class Meta:
        constraints = [
            # TODO this may no longer be necessary with pipeline run
            UniqueConstraint(
                fields=[
                    "pulsar_fold_result",
                    "file_type",
                ],
                name="Unique file type for a PulsarFoldResult"
            )
        ]

class Toa(models.Model):
    # foreign keys
    pipeline_run = models.ForeignKey(PipelineRun, models.CASCADE, related_name="toas")
    observation = models.ForeignKey(Observation, models.CASCADE, related_name="toas")
    project = models.ForeignKey(Project, models.CASCADE)
    ephemeris = models.ForeignKey(Ephemeris, models.CASCADE)
    template = models.ForeignKey(Template, models.CASCADE)

    # toa results
    archive = models.CharField(max_length=128)
    freq_MHz = models.FloatField()
    mjd = models.DecimalField(decimal_places=12, max_digits=18)
    mjd_err = models.FloatField()
    telescope = models.CharField(max_length=32)

    # The flags from the toa file
    fe = models.CharField(max_length=32, null=True)
    be = models.CharField(max_length=32, null=True)
    f = models.CharField(max_length=32, null=True)
    bw = models.IntegerField(null=True)
    tobs = models.IntegerField(null=True)
    tmplt = models.CharField(max_length=128, null=True)
    gof = models.FloatField(null=True)
    nbin = models.IntegerField(null=True)
    nch = models.IntegerField(null=True)
    chan = models.IntegerField(null=True)
    rcvr = models.CharField(max_length=32, null=True)
    snr = models.FloatField(null=True)
    length = models.IntegerField(null=True)
    subint = models.IntegerField(null=True)

    # Flags for the type of TOA (used for filtering downloads)
    dm_corrected  = models.BooleanField(default=False)
    minimum_nsubs = models.BooleanField(default=False)
    maximum_nsubs = models.BooleanField(default=False)
    obs_nchan = models.IntegerField(null=True)
    obs_npol = models.IntegerField(default=4)

    # Residual fields
    # X axis types
    # mjd should be same as toa
    day_of_year = models.FloatField(null=True)
    binary_orbital_phase = models.FloatField(null=True)

    # Y axis types
    residual_sec = models.FloatField(null=True)
    residual_sec_err = models.FloatField(null=True)
    residual_phase = models.FloatField(null=True) # pulse period phase
    residual_phase_err = models.FloatField(null=True)

    @classmethod
    def get_query(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    @classmethod
    def bulk_create(
            cls,
            pipeline_run_id,
            project_short,
            template_id,
            ephemeris_text,
            toa_lines,
            dm_corrected,
            minimum_nsubs,
            maximum_nsubs,
            npol,
            nchan,
        ):
        pipeline_run = PipelineRun.objects.get(id=pipeline_run_id)
        observation  = pipeline_run.observation
        project      = Project.objects.get(short=project_short)
        template     = Template.objects.get(id=template_id)

        ephemeris_dict = parse_ephemeris_file(ephemeris_text)
        try:
            ephemeris, _ = Ephemeris.objects.get_or_create(
                pulsar=observation.pulsar,
                project=project,
                # TODO add created_by
                ephemeris_data=json.dumps(ephemeris_dict),
                p0=ephemeris_dict["P0"],
                dm=ephemeris_dict["DM"],
                valid_from=ephemeris_dict["START"],
                valid_to=ephemeris_dict["FINISH"],
            )
        except IntegrityError:
            # Handle the IntegrityError gracefully by grabbing the already created ephem
            ephemeris = Ephemeris.objects.get(
                pulsar=observation.pulsar,
                project=project,
                ephemeris_data=json.dumps(ephemeris_dict),
            )

        # created_toas = []
        toas_to_create = []
        for toa_line in toa_lines:
            if "FORMAT" in toa_line:
                continue
            toa_line = toa_line.rstrip("\n")
            # Loop over toa lines and turn into a dict
            toa_dict = toa_line_to_dict(toa_line)
            # Revert it back to a line and check it matches before uploading
            output_toa_line = toa_dict_to_line(toa_dict)
            if toa_line != output_toa_line:
                raise GraphQLError(f"Assertion failed. toa_line and output_toa_line do not match.\n{toa_line}\n{output_toa_line}")
            # Info only for Meerkat Toas
            if project_short == "MONSPSR_TIMING":
                nch = None
                chan = None
                rcvr = None
                length = None
                subint = None
            else:
                nch = toa_dict["nch"]
                chan = toa_dict["chan"]
                rcvr = toa_dict["rcvr"]
                length = toa_dict["length"]
                subint = toa_dict["subint"]

            # Upload the toa
            toas_to_create.append(
                Toa(
                    pipeline_run =pipeline_run,
                    observation  =observation,
                    project      =project,
                    ephemeris    =ephemeris,
                    template     =template,
                    archive      =toa_dict["archive"],
                    freq_MHz     =toa_dict["freq_MHz"],
                    mjd          =toa_dict["mjd"],
                    mjd_err      =toa_dict["mjd_err"],
                    telescope    =toa_dict["telescope"],
                    fe           =toa_dict["fe"],
                    be           =toa_dict["be"],
                    f            =toa_dict["f"],
                    bw           =toa_dict["bw"],
                    tobs         =toa_dict["tobs"],
                    tmplt        =toa_dict["tmplt"],
                    gof          =toa_dict.get("gof", None),
                    nbin         =toa_dict["nbin"],
                    snr          =toa_dict["snr"],
                    nch          =nch,
                    chan         =chan,
                    rcvr         =rcvr,
                    length       =length,
                    subint       =subint,
                    dm_corrected =dm_corrected,
                    minimum_nsubs=minimum_nsubs,
                    maximum_nsubs=maximum_nsubs,
                    obs_nchan    =nchan,
                    obs_npol     =npol,
                )
            )
        created_toas = Toa.objects.bulk_create(
            toas_to_create,
            update_conflicts=True,
            unique_fields=[
                "observation",
                "project",
                "dm_corrected",
                "obs_npol",
                # Frequency
                "obs_nchan", # Number of channels
                "chan", # Chan ID
                # Time
                "minimum_nsubs",
                "maximum_nsubs",
                "subint", # Time ID
            ],
            update_fields=[
                "pipeline_run",
                "observation",
                "project",
                "ephemeris",
                "template",
                "archive",
                "freq_MHz",
                "mjd",
                "mjd_err",
                "telescope",
                "fe",
                "be",
                "f",
                "bw",
                "tobs",
                "tmplt",
                "gof",
                "nbin",
                "nch",
                "chan",
                "rcvr",
                "snr",
                "length",
                "subint",
                "dm_corrected",
                "minimum_nsubs",
                "maximum_nsubs",
                "obs_nchan",
                "obs_npol",
            ],
        )
        return created_toas

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    "observation",
                    "project",
                    "dm_corrected",
                    "obs_npol",
                    # Frequency
                    "obs_nchan", # Number of channels
                    "chan", # Chan ID
                    # Time
                    "minimum_nsubs",
                    "maximum_nsubs",
                    "subint", # Time ID
                ],
                name="Unique ToA for observations, project and type of ToA (decimations)."
            )
        ]
