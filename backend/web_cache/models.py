import math
from datetime import datetime
from dateutil import parser
from django.db import models
from dataportal.models import Foldings, Observations, Filterbankings, Sessions
from django_mysql.models import JSONField
from statistics import mean

BAND_CHOICES = (('L-Band', 'L-Band'), ('S-Band', 'S-Band'), ('UHF', 'UHF'), ('UNKNOWN', 'Unknown'))


class BasePulsar(models.Model):
    """
    Abstract class to store common methods and attributes that Searchmode and Foldings share.
    """

    main_project = models.CharField(max_length=64)
    project = models.CharField(max_length=500)
    band = models.CharField(choices=BAND_CHOICES, max_length=7)
    jname = models.CharField(max_length=64)
    latest_observation = models.DateTimeField()
    first_observation = models.DateTimeField()
    timespan = models.IntegerField()
    number_of_observations = models.IntegerField()
    beam = models.CharField(max_length=16)

    class Meta:
        abstract = True
        ordering = ["-latest_observation"]

    @classmethod
    def get_query(cls, **kwargs):
        if 'band' in kwargs and kwargs['band'] == 'All':
            kwargs.pop('band')

        if 'project' in kwargs and kwargs['project'] == 'All':
            kwargs.pop('project')
        elif 'project' in kwargs:
            kwargs["project__icontains"] = kwargs.pop('project')

        if 'main_project' in kwargs and kwargs['main_project'] == 'All':
            kwargs.pop('main_project')

        return cls.objects.filter(**kwargs)

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
            "L-Band": {"centre_frequency": 1285.0, "allowed_deviation": 200.0},
            "S-Band": {"centre_frequency": 2625.0, "allowed_deviation": 200.0},
        }

        # For band check to work the frequency must be either an int or a float.
        for band in bands.keys():
            if abs(float(frequency) - bands[band]["centre_frequency"]) < bands[band]["allowed_deviation"]:
                return band

        return 'UNKNOWN'

    @classmethod
    def get_by_session(cls, session):
        return cls.objects.filter(latest_observation__range=(session.start, session.end))


class SearchmodePulsar(BasePulsar):
    @classmethod
    def update_or_create(cls, target):
        raw_observations = Observations.objects.filter(target=target)

        filterbankings = Filterbankings.objects.filter(processing__observation__in=raw_observations).order_by(
            "-processing__observation__utc_start"
        )

        observation_ids = [f.processing.observation.id for f in filterbankings]
        target_observations = raw_observations.filter(id__in=observation_ids)

        latest_observation = target_observations.order_by('-utc_start').first().utc_start
        first_observation = target_observations.order_by('-utc_start').last().utc_start
        timespan = (latest_observation - first_observation).days + 1
        number_of_observations = target_observations.count()

        projects = ", ".join({observation.project.short for observation in target_observations})

        try:
            main_project = latest_observation.project.program.name
        except AttributeError:
            main_project = 'UNKNOWN'

        return SearchmodePulsar.objects.update_or_create(
            main_project=main_project,
            jname=target.name,
            defaults={
                "project": projects,
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
    last_integration_minutes = models.FloatField(null=True)

    @property
    def session(self):
        return Sessions.get_session(self.latest_observation)

    @classmethod
    def update_or_create(cls, pulsar, program_name):
        """
        Processes data from multiple tables into a single source that can be consumed directly
        by the web application through graphql.

        Parameters:
            folding: A Foldings model instance.
        """

        # Get various related model objects required using the saved folding instance as a base.
        foldings = Foldings.objects.filter(
            folding_ephemeris__pulsar=pulsar, processing__observation__project__program__name=program_name
        )

        if not foldings:
            return

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
            / 60
            / 60
        )
        last_sn_raw = results['snr'] if 'snr' in results else 0
        last_integration_minutes = latest_folding_observation.processing.observation.duration / 60

        projects = ", ".join({observation.project.short for observation in folding_observations})

        return FoldPulsar.objects.update_or_create(
            main_project=program_name,
            jname=pulsar.jname,
            defaults={
                "project": projects,
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


class FoldDetailImage(models.Model):
    fold_pulsar_detail = models.ForeignKey("FoldPulsarDetail", related_name='images', on_delete=models.CASCADE)
    image_type = models.CharField(max_length=64, null=True)
    url = models.URLField()

    @property
    def plot_type(self):
        return self.image_type.split('.')[-2]

    @property
    def resolution(self):
        # Resolution is either 'hi', 'lo' or size in the form '300x240'
        # We will assume anything with a height lower than 600 is 'lo' res
        try:
            resolution = self.image_type.split('.')[-1]
            return 'lo' if int(resolution.split('x')[0]) < 600 else 'hi'
        except ValueError:
            return self.image_type.split('.')[-1]

    @property
    def process(self):
        image_details = self.image_type.split('.')
        return image_details[0] if len(image_details) > 2 else 'raw'


class FoldPulsarDetail(models.Model):
    fold_pulsar = models.ForeignKey(FoldPulsar, on_delete=models.CASCADE)
    utc = models.DateTimeField()
    project = models.CharField(max_length=50)
    proposal = models.CharField(max_length=40)
    ephemeris = JSONField()
    ephemeris_is_updated_at = models.DateTimeField(null=True)
    length = models.FloatField(null=True)
    beam = models.IntegerField()
    bw = models.DecimalField(max_digits=12, decimal_places=2)
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
    tsubint = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    schedule = models.CharField(max_length=16, null=True)
    phaseup = models.CharField(max_length=16, null=True)
    frequency = models.DecimalField(null=True, max_digits=15, decimal_places=9)
    npol = models.IntegerField(null=True)

    class Meta:
        ordering = ["-utc"]

    @property
    def estimated_size(self):
        """Estimated size of the observation data stored on disk in bytes."""
        try:
            return math.ceil(self.length / float(self.tsubint)) * self.nbin * self.nchan * self.npol * 2
        except ZeroDivisionError:
            return 0

    @property
    def jname(self):
        return self.fold_pulsar.jname

    @property
    def session(self):
        return Sessions.get_session(self.utc)

    @classmethod
    def update_or_create(cls, folding):
        pulsar = folding.folding_ephemeris.pulsar
        observation = folding.processing.observation

        if not observation.project.program:
            return

        main_project = observation.project.program.name

        try:
            fold_pulsar = FoldPulsar.objects.get(jname=pulsar.jname, main_project=main_project)
        except FoldPulsar.DoesNotExist:
            print("FoldPulsar ", pulsar.jname, main_project, " does not exist")
            return

        results = folding.processing.results if folding.processing.results else {}

        new_fold_pulsar_detail, created = FoldPulsarDetail.objects.update_or_create(
            fold_pulsar=fold_pulsar,
            utc=observation.utc_start,
            defaults={
                "project": observation.project.short,
                "proposal": observation.project.code,
                "ephemeris": folding.folding_ephemeris.ephemeris,
                "ephemeris_is_updated_at": folding.folding_ephemeris.created_at,
                "length": observation.duration,
                "beam": observation.instrument_config.beam,
                "bw": observation.instrument_config.bandwidth,
                "ra": observation.target.raj,
                "dec": observation.target.decj,
                "nchan": folding.nchan,
                "tsubint": folding.tsubint,
                "band": fold_pulsar.get_band(observation.instrument_config.frequency),
                "nbin": folding.nbin,
                "nant": observation.nant,
                "nant_eff": observation.nant_eff,
                "dm_fold": folding.dm,
                "dm_meerpipe": results.get('dm_meerpipe', None),
                "rm_meerpipe": results.get('rm_meerpipe', None),
                "sn_backend": results.get('snr', None),
                "sn_meerpipe": results.get('sn_meerpipe', None),
                "schedule": "12",
                "phaseup": "12",
                "frequency": observation.instrument_config.frequency,
                "npol": observation.instrument_config.npol,
            },
        )

        # Find all TOA entries with a matching fold_id. These TOA entries should each link back to an entry in
        # processings, with only one processing per pipeline (i.e. project code). Those processing entries than link
        # forwards to the pipelineimages table.
        for toas in folding.toas_set.all():
            for image in toas.processing.pipelineimages_set.all():
                FoldDetailImage.objects.update_or_create(
                    fold_pulsar_detail=new_fold_pulsar_detail,
                    image_type=image.image_type,
                    defaults={"url": image.image.name},
                )
        # Also process the raw images
        for image in folding.processing.pipelineimages_set.all():
            FoldDetailImage.objects.update_or_create(
                fold_pulsar_detail=new_fold_pulsar_detail,
                image_type=image.image_type,
                defaults={"url": image.image.name},
            )

        return new_fold_pulsar_detail, created

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
    length = models.FloatField(null=True)
    beam = models.IntegerField()
    frequency = models.DecimalField(max_digits=50, decimal_places=8)
    nchan = models.IntegerField()
    nbit = models.IntegerField()
    nant_eff = models.IntegerField(null=True)
    npol = models.IntegerField()
    dm = models.DecimalField(max_digits=12, decimal_places=2)
    tsamp = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-utc"]

    @classmethod
    def update_or_create(cls, filter_bankings):
        observation = filter_bankings.processing.observation
        searchmode_pulsar = SearchmodePulsar.objects.get(jname=observation.target.name)
        return cls.objects.update_or_create(
            searchmode_pulsar=searchmode_pulsar,
            utc=filter_bankings.processing.observation.utc_start,
            defaults={
                "project": observation.project.short,
                "ra": observation.target.raj,
                "dec": observation.target.decj,
                "length": observation.duration,
                "beam": observation.instrument_config.beam,
                "frequency": observation.instrument_config.frequency,
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


class SessionDisplay(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    number_of_observations = models.IntegerField()
    number_of_pulsars = models.IntegerField()
    list_of_pulsars = models.TextField(null=True)
    frequency = models.FloatField(null=True)
    projects = models.CharField(max_length=2000, null=True)
    total_integration = models.IntegerField()
    n_dish_min = models.IntegerField(null=True)
    n_dish_max = models.IntegerField(null=True)
    zap_fraction = models.FloatField(null=True)

    class Meta:
        ordering = ["-start"]

    @classmethod
    def update_or_create(cls, session):
        session_pulsars = SessionPulsar.objects.filter(
            session_display__start=session.start, session_display__end=session.end
        )

        number_of_observations = 0

        n_dish_max = None
        n_dish_min = None

        for session_pulsar in session_pulsars.all():
            if session_pulsar.fold_pulsar:
                number_of_observations += session_pulsar.fold_pulsar.foldpulsardetail_set.filter(
                    utc__range=(session.start, session.end)
                ).count()
                min_nant_eff, max_nant_eff = (
                    session_pulsar.fold_pulsar.foldpulsardetail_set.filter(utc__range=(session.start, session.end))
                    .aggregate(models.Min('nant_eff'), models.Max('nant_eff'))
                    .values()
                )

                if n_dish_min:
                    n_dish_min = min_nant_eff if n_dish_min > min_nant_eff else n_dish_min
                else:
                    n_dish_min = min_nant_eff

                if n_dish_max:
                    n_dish_max = max_nant_eff if n_dish_max < max_nant_eff else n_dish_max
                else:
                    n_dish_max = max_nant_eff

            if session_pulsar.search_pulsar:
                number_of_observations += session_pulsar.search_pulsar.searchmodepulsardetail_set.filter(
                    utc__range=(session.start, session.end)
                ).count()
                min_nant_eff, max_nant_eff = (
                    session_pulsar.search_pulsar.searchmodepulsardetail_set.filter(
                        utc__range=(session.start, session.end)
                    )
                    .aggregate(models.Min('nant_eff'), models.Max('nant_eff'))
                    .values()
                )

                if n_dish_min:
                    n_dish_min = min_nant_eff if n_dish_min > min_nant_eff else n_dish_min
                else:
                    n_dish_min = min_nant_eff

                if n_dish_max:
                    n_dish_max = max_nant_eff if n_dish_max < max_nant_eff else n_dish_max
                else:
                    n_dish_max = max_nant_eff

        projects = ', '.join({session_pulsar.project for session_pulsar in session_pulsars})

        list_of_pulsars = ', '.join(
            set.union(
                {session_pulsar.fold_pulsar.jname for session_pulsar in session_pulsars if session_pulsar.fold_pulsar},
                {
                    session_pulsar.search_pulsar.jname
                    for session_pulsar in session_pulsars
                    if session_pulsar.search_pulsar
                },
            )
        )

        total_integration = sum([session.integrations for session in session_pulsars])

        # Because we only create a new session per start time we need to work out if we need to keep the old end or use
        # the new one based on which is later. This is fixes an issue with the way Sessions are created in the ingest.
        try:
            current_end = cls.objects.get(start=session.start).end
            end = current_end if current_end > session.end else session.end
        except cls.DoesNotExist:
            end = session.end

        return cls.objects.update_or_create(
            start=session.start,
            defaults={
                "end": end,
                "number_of_observations": number_of_observations,
                "frequency": getattr(session_pulsars.filter(frequency__isnull=False).first(), 'frequency', None),
                "number_of_pulsars": session_pulsars.count(),
                "list_of_pulsars": list_of_pulsars,
                "projects": projects,
                "total_integration": total_integration,
                "n_dish_min": n_dish_min,
                "n_dish_max": n_dish_max,
                "zap_fraction": 0,
            },
        )

    @classmethod
    def get_query(cls, **kwargs):
        return cls.objects.filter(number_of_observations__gt=0, **kwargs)

    @classmethod
    def get_last_session(cls):
        return cls.objects.first()

    @classmethod
    def get_query_instance(cls, **kwargs):
        if 'project' in kwargs and kwargs['project'] == 'All':
            kwargs.pop('project')

        if 'start' in kwargs and 'end' in kwargs:
            kwargs['start'] = parser.parse(kwargs.get('start', ''))
            kwargs['end'] = parser.parse(kwargs.get('end', ''))
            return cls.objects.get(**kwargs)

        elif 'utc' in kwargs:
            utc = parser.parse(kwargs.pop('utc'))
            return cls.objects.get(start__lte=utc, end__gte=utc)

        else:
            return cls.get_last_session()

    def get_session_pulsars(self, **kwargs):
        if 'project' in kwargs and kwargs['project'] == 'All':
            kwargs.pop('project')

        return self.sessionpulsar_set.filter(**kwargs)


class SessionPulsar(models.Model):
    session_display = models.ForeignKey(SessionDisplay, on_delete=models.CASCADE)
    fold_pulsar = models.ForeignKey(FoldPulsar, null=True, on_delete=models.CASCADE)
    search_pulsar = models.ForeignKey(SearchmodePulsar, null=True, on_delete=models.CASCADE)
    utc = models.DateTimeField()
    project = models.CharField(max_length=50)
    backendSN = models.IntegerField(null=True)
    integrations = models.IntegerField()
    beam = models.IntegerField()
    frequency = models.DecimalField(max_digits=50, decimal_places=8)
    phase_vs_time_hi = models.URLField(null=True)
    phase_vs_frequency_hi = models.URLField(null=True)
    profile_hi = models.URLField(null=True)
    phase_vs_time_lo = models.URLField(null=True)
    phase_vs_frequency_lo = models.URLField(null=True)
    profile_lo = models.URLField(null=True)

    class Meta:
        ordering = ["-session_display__start"]

    @property
    def jname(self):
        return self.fold_pulsar.jname

    @property
    def pulsar_type(self):
        return 'search' if self.search_pulsar else 'fold'

    @classmethod
    def update_or_create(cls, session, pulsar):
        if isinstance(pulsar, SearchmodePulsar):
            last_observation = pulsar.searchmodepulsardetail_set.filter(utc__range=(session.start, session.end)).last()
            images = {}
            fold_pulsar = None
            search_pulsar = pulsar
        else:
            last_observation = pulsar.foldpulsardetail_set.filter(utc__range=(session.start, session.end)).last()
            images = {i.image_type: i.url for i in last_observation.images.all()}
            fold_pulsar = pulsar
            search_pulsar = None

        if not last_observation:
            return False, None

        return cls.objects.update_or_create(
            session_display=session,
            fold_pulsar=fold_pulsar,
            search_pulsar=search_pulsar,
            defaults={
                "utc": last_observation.utc,
                "project": last_observation.project,
                "backendSN": getattr(last_observation, 'sn_backend', None),
                "integrations": last_observation.length,
                "beam": last_observation.beam,
                "frequency": last_observation.frequency,
                "phase_vs_frequency_hi": images.get('freq.hi', None),
                "phase_vs_time_hi": images.get('time.hi', None),
                "profile_hi": images.get('profile.hi', None),
                "phase_vs_frequency_lo": images.get('freq.lo', None),
                "phase_vs_time_lo": images.get('time.lo', None),
                "profile_lo": images.get('profile.lo', None),
            },
        )
