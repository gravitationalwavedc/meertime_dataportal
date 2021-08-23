import math
import ntpath
from datetime import datetime
from django.utils.timezone import make_aware
from django.db import models
from dataportal.models import Foldings, Observations, Filterbankings
from django_mysql.models import JSONField
from dataportal import storage
from statistics import mean

BAND_CHOICES = (('L-BAND', 'L-Band'), ('S-BAND', 'S-Band'), ('UHF', 'UHF'), ('UNKNOWN', 'Unknown'))

MAIN_PROJECT_CHOICES = (('MEERTIME', 'MeerTime'), ('TRAPUM', 'Trapum'), ('UNKNOWN', 'UNKNOWN'))


class BasePulsar(models.Model):
    """
    Abstract class to store common methods and attributes that Searchmode and Foldings share.
    """

    main_project = models.CharField(choices=MAIN_PROJECT_CHOICES, max_length=8)
    project = models.CharField(max_length=50)
    band = models.CharField(choices=BAND_CHOICES, max_length=7)
    jname = models.CharField(max_length=64, unique=True)
    latest_observation = models.DateTimeField()
    first_observation = models.DateTimeField()
    timespan = models.IntegerField()
    number_of_observations = models.IntegerField()
    beam = models.CharField(max_length=16)

    class Meta:
        abstract = True

    @classmethod
    def get_query(cls, **kwargs):
        if 'band' in kwargs and kwargs['band'] == 'All':
            kwargs.pop('band')

        if 'project' in kwargs and kwargs['project'] == 'All':
            kwargs.pop('project')

        if 'main_project' in kwargs and kwargs['main_project'] == 'All':
            kwargs.pop('main_project')

        return cls.objects.filter(**kwargs)

    @classmethod
    def get_main_project(cls, project_code):
        if project_code.startswith('SCI') and 'MK' in project_code:
            return 'TRAPUM'

        if project_code.startswith('SCI') and 'MB' in project_code:
            return 'MEERTIME'

        return 'UNKNOWN'

    @classmethod
    def get_band(cls, frequency):
        """
        Band is the string representation of the frequency used by astronomers.

        There are 3 bands that most frequencies should fit into.
        UHF: Ultra High Frequency / 50-cm band, in the range 300 MHZ to 1 GHZ
        L-band: 20-cm band, around Hydrogen transition line ~1.42 GHz
        S-band: 10-cm band, around 2.6 GHz
        """
        bands = {
            "UHF": {"centre_frequency": 830.0, "allowed_deviation": 200.0},
            "L-BAND": {"centre_frequency": 1285.0, "allowed_deviation": 200.0},
            "S-BAND": {"centre_frequency": 2625.0, "allowed_deviation": 200.0},
        }

        # For band check to work the frequency must be either an int or a float.
        if type(frequency) in [float, int]:
            for band in bands.keys():
                if abs(frequency - bands[band]["centre_frequency"]) < bands[band]["allowed_deviation"]:
                    return band

        return 'UNKNOWN'


class SearchmodePulsar(BasePulsar):
    @classmethod
    def update_or_create(cls, pulsar):
        pulsar_targets = pulsar.pulsartargets_set.all()
        targets = [p.target for p in pulsar_targets]
        pulsar_observations = Observations.objects.filter(target__in=targets)

        latest_filterbankings = (
            Filterbankings.objects.filter(processing__observation__in=pulsar_observations)
            .order_by("-processing__observation__utc_start")
            .last()
        )
        latest_filterbankings_observation = latest_filterbankings.processing.observation

        latest_observation = pulsar_observations.order_by('-utc_start').first().utc_start
        first_observation = pulsar_observations.order_by('-utc_start').last().utc_start
        timespan = (latest_observation - first_observation).days + 1
        number_of_observations = pulsar_observations.count()

        SearchmodePulsar.objects.update_or_create(
            main_project=cls.get_main_project(latest_filterbankings_observation.project.code),
            project=latest_filterbankings_observation.project.short,
            jname=pulsar.jname,
            defaults={
                "latest_observation": latest_observation,
                "first_observation": first_observation,
                "timespan": timespan,
                "number_of_observations": number_of_observations,
            },
        )


class FoldPulsar(BasePulsar):
    total_integration_hours = models.DecimalField(max_digits=12, decimal_places=1)
    last_sn_raw = models.DecimalField(max_digits=12, decimal_places=1)
    avg_sn_pipe = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    max_sn_pipe = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    last_integration_minutes = models.DecimalField(max_digits=12, decimal_places=1)

    @classmethod
    def update_or_create(cls, pulsar):
        """
        Processes data from multiple tables into a single source that can be consumed directly
        by the web application through graphql.

        Parameters:
            folding: A Foldings model instance.
        """

        # Get various related model objects required using the saved folding instance as a base.
        foldings = Foldings.objects.filter(folding_ephemeris__pulsar=pulsar)
        folding_observations = [folding.processing.observation for folding in foldings]
        latest_folding_observation = foldings.order_by("-processing__observation__utc_start").first()

        results = latest_folding_observation.processing.results

        # Process data
        latest_observation = (
            foldings.order_by('-processing__observation__utc_start').first().processing.observation.utc_start
        )

        first_observation = (
            foldings.order_by('-processing__observation__utc_start').last().processing.observation.utc_start
        )

        timespan = (latest_observation - first_observation).days + 1
        number_of_observations = foldings.count()
        total_integration_hours = (
            sum(
                [
                    folding.processing.observation.duration
                    for folding in foldings
                    if folding.processing.observation.duration
                ]
            )
            / 120
        )
        last_sn_raw = results['snr'] if 'snr' in results else 0
        last_integration_minutes = latest_folding_observation.processing.observation.duration

        FoldPulsar.objects.update_or_create(
            main_project=cls.get_main_project(latest_folding_observation.processing.observation.project.code),
            project=latest_folding_observation.processing.observation.project.short,
            jname=pulsar.jname,
            defaults={
                "band": cls.get_band(latest_folding_observation.processing.observation.instrument_config.frequency),
                "latest_observation": latest_observation,
                "first_observation": first_observation,
                "timespan": timespan,
                "number_of_observations": number_of_observations,
                "total_integration_hours": total_integration_hours,
                "last_sn_raw": last_sn_raw,
                "last_integration_minutes": last_integration_minutes if last_integration_minutes else 0,
                "avg_sn_pipe": cls.get_average_snr_over_5min(folding_observations),
                "max_sn_pipe": cls.get_max_snr_over_5min(folding_observations),
                "beam": latest_folding_observation.processing.observation.instrument_config.beam,
            },
        )

    @classmethod
    def get_snr_results(cls, pulsar_observations):
        observation_results = []
        for observation in pulsar_observations:
            for process in observation.processings_set.all():
                if 'snr' in process.results and 'length' in process.results:
                    observation_results.append({'snr': process.results['snr'], 'length': observation.duration})
        return observation_results

    @classmethod
    def get_average_snr_over_5min(cls, pulsar_observations):
        # SNR is proportional to the sqrt of the observation length.
        # To get the average SNR from a 5 minute block of observations we calculate the observation snr / sqrt And
        observation_results = cls.get_snr_results(pulsar_observations)

        if not observation_results:
            return None

        sqrt_300 = 17.3205080757

        return mean([(o['snr'] / math.sqrt(o['length']) * sqrt_300) for o in observation_results])

    @classmethod
    def get_max_snr_over_5min(cls, pulsar_observations):
        observation_results = cls.get_snr_results(pulsar_observations)

        if not observation_results:
            return None

        sqrt_300 = 17.3205080757

        return max([(o['snr'] / math.sqrt(o['length']) * sqrt_300) for o in observation_results])


class FoldPulsarDetail(models.Model):
    fold_pulsar = models.ForeignKey(FoldPulsar, on_delete=models.CASCADE)
    utc = models.DateTimeField()
    project = models.CharField(max_length=50)
    proposal = models.CharField(max_length=40)
    ephemeris = JSONField()
    ephemeris_is_updated_at = models.DateTimeField(null=True)
    length = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    beam = models.IntegerField()
    bw_mhz = models.DecimalField(max_digits=12, decimal_places=2)
    nchan = models.IntegerField()
    band = models.CharField(choices=BAND_CHOICES, max_length=7)
    nbin = models.IntegerField()
    nant = models.IntegerField(null=True)
    nant_eff = models.IntegerField(null=True)
    dm_fold = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    dm_meerpipe = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    rm_meerpipe = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    sn_backend = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    sn_meerpipe = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    ra = models.CharField(max_length=16, null=True)
    dec = models.CharField(max_length=16, null=True)
    nsubint = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    schedule = models.CharField(max_length=16, null=True)
    phaseup = models.CharField(max_length=16, null=True)
    phase_vs_time = models.URLField(null=True)
    phase_vs_frequency = models.URLField(null=True)
    bandpass = models.URLField(null=True)
    snr_vs_time = models.URLField(null=True)
    profile = models.URLField(null=True)
    frequency = models.DecimalField(null=True, max_digits=15, decimal_places=9)

    @classmethod
    def update_or_create(cls, folding):
        pulsar = folding.folding_ephemeris.pulsar
        fold_pulsar = FoldPulsar.objects.get(jname=pulsar.jname)
        observation = folding.processing.observation

        # Images are currently stored in the database with the wrong path. I suspect this is because of the way the
        # CLI is processing the image itself. We fix this here by manually setting the correct url. This will
        # break if the way images are stored on the server change.
        # To get the correct filename we use ntpath to extract it from the path given by the image.name property.
        images = {
            pipelineimage.image_type: storage.get_upload_location(
                pipelineimage, ntpath.basename(pipelineimage.image.name)
            )
            for pipelineimage in folding.processing.pipelineimages_set.all()
        }

        # Known image types are 'band', 'snrt', 'freq', 'time', and 'flux'.
        bandpass = images['band'] if 'band' in images else None
        phase_vs_time = images['time'] if 'time' in images else None
        phase_vs_frequency = images['freq'] if 'freq' in images else None
        snr_vs_time = images['snrt'] if 'snrt' in images else None
        profile = images['flux'] if 'flux' in images else None

        FoldPulsarDetail.objects.update_or_create(
            fold_pulsar=fold_pulsar,
            utc=observation.utc_start,
            defaults={
                "project": observation.project.short,
                "proposal": observation.project.code,
                "ephemeris": folding.folding_ephemeris.ephemeris,
                "ephemeris_is_updated_at": folding.folding_ephemeris.created_at,
                "length": observation.duration,
                "beam": observation.instrument_config.beam,
                "bw_mhz": observation.instrument_config.bandwidth,
                "ra": observation.target.raj,
                "dec": observation.target.decj,
                "nchan": folding.nchan,
                "nsubint": folding.tsubint,
                "band": fold_pulsar.get_band(observation.instrument_config.frequency),
                "nbin": folding.nbin,
                "nant": observation.nant,
                "nant_eff": observation.nant_eff,
                "dm_fold": folding.dm,
                "dm_meerpipe": 0,
                "rm_meerpipe": 0,
                "sn_backend": folding.processing.results['snr'],
                "sn_meerpipe": 0,
                "schedule": "12",
                "phaseup": "12",
                "phase_vs_time": phase_vs_time,
                "phase_vs_frequency": phase_vs_frequency,
                "bandpass": bandpass,
                "snr_vs_time": snr_vs_time,
                "profile": profile,
                "frequency": observation.instrument_config.frequency,
            },
        )

    @classmethod
    def get_query(cls, **kwargs):
        if 'jname' in kwargs:
            kwargs['fold_pulsar__jname'] = kwargs.pop('jname')

        if 'main_project' in kwargs:
            kwargs['fold_pulsar__main_project'] = kwargs.pop('main_project')

        if 'utc' in kwargs:
            kwargs['utc'] = datetime.strptime(kwargs['utc'], '%Y-%m-%d-%H:%M:%S')

        return cls.objects.filter(**kwargs)


class SearchmodePulsarDetail(models.Model):
    searchmode_pulsar = models.ForeignKey(SearchmodePulsar, on_delete=models.CASCADE)
    utc = models.DateTimeField()
    project = models.CharField(max_length=50)
    ra = models.CharField(max_length=16)
    dec = models.CharField(max_length=16)
    length = models.DecimalField(max_digits=12, decimal_places=1)
    beam = models.IntegerField()
    frequency = models.DecimalField(max_digits=50, decimal_places=8)
    nchan = models.IntegerField()
    nbit = models.IntegerField()
    nant_eff = models.IntegerField(null=True)
    npol = models.IntegerField()
    dm = models.DecimalField(max_digits=12, decimal_places=2)
    tsamp = models.DecimalField(max_digits=12, decimal_places=2)

    @classmethod
    def update_or_create(cls, filter_bankings):
        observation = filter_bankings.processing.observation
        searchmode_pulsar = SearchmodePulsar.objects.get(jname=observation.target.name)
        SearchmodePulsarDetail.objects.update_or_create(
            searchmode_pulsar=searchmode_pulsar,
            utc=filter_bankings.processing.observation.utc_start,
            defaults={
                "project": observation.project,
                "ra": observation.target.raj,
                "dec": observation.target.decj,
                "length": observation.duration,
                "beam": observation.instrument_config.beam,
                "frequency": 0,
                "nchan": filter_bankings.nchan,
                "nbit": filter_bankings.nbit,
                "nant_eff": observation.nant_eff,
                "npol": filter_bankings.npol,
                "dm": filter_bankings.dm,
                "tsamp": filter_bankings.tsamp,
            },
        )

    @classmethod
    def get_query(cls, **kwargs):
        if 'jname' in kwargs:
            kwargs['searchmode_pulsar__jname'] = kwargs.pop('jname')

        if 'project' in kwargs:
            kwargs['searchmode_pulsar__main_project'] = kwargs.pop('project')

        return cls.objects.filter(**kwargs)