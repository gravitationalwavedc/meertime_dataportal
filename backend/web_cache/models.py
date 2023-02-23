import math
from collections import Counter
from datetime import datetime
from dateutil import parser
from django.db import models
from dataportal.models import Foldings, Observations, Filterbankings, Sessions, Processings, Pipelinefiles
from django.db.models import JSONField
from statistics import mean
from web_cache.plot_types import PLOT_NAMES

BAND_CHOICES = (('L-Band', 'L-Band'), ('S-Band', 'S-Band'), ('UHF', 'UHF'), ('UNKNOWN', 'Unknown'))


class BasePulsar(models.Model):
    """
    Abstract class to store common methods and attributes that Searchmode and Foldings share.
    """

    main_project = models.CharField(max_length=64)
    project = models.CharField(max_length=500)
    all_projects = models.CharField(max_length=500)
    band = models.CharField(choices=BAND_CHOICES, max_length=50)
    jname = models.CharField(max_length=64)
    latest_observation = models.DateTimeField()
    first_observation = models.DateTimeField()
    timespan = models.IntegerField()
    number_of_observations = models.IntegerField()
    beam = models.CharField(max_length=16)
    comment = models.TextField(null=True)

    class Meta:
        abstract = True
        ordering = ["-latest_observation"]

    @classmethod
    def get_query(cls, **kwargs):
        if 'band' in kwargs:
            if kwargs['band'] == 'All':
                kwargs.pop('band')
            else:
                kwargs["band__icontains"] = kwargs.pop('band')

        if 'project' in kwargs:
            if kwargs['project'] == 'All':
                kwargs.pop('project')
            else:
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

        return next((
            band for band, frequencies in bands.items()
            if abs(float(frequency) - frequencies["centre_frequency"]) < frequencies["allowed_deviation"]
        ), "UNKNOWN")

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

        all_projects = ", ".join({observation.project.short for observation in target_observations})

        project_counts = {}

        for observation in target_observations:
            # If you like it, then you should have put a key on it.
            project_short = observation.project.short
            if project_short in project_counts:
                # I'm a survivor, I'm not a quitter, I'm gonna increment until I'm a winner.
                project_counts[project_short] += 1
            else:
                project_counts[project_short] = 1

        # To the left, to the left
        # Find the key with the highest count, to the left
        most_common_project = max(project_counts, key=project_counts.get)

        try:
            main_project = latest_observation.project.program.name
        except AttributeError:
            main_project = 'meertime'

        return SearchmodePulsar.objects.update_or_create(
            main_project=main_project,
            jname=target.name,
            defaults={
                "all_projects": all_projects,
                "project": most_common_project,
                "latest_observation": latest_observation,
                "first_observation": first_observation,
                "timespan": timespan,
                "number_of_observations": number_of_observations,
            },
        )


class FoldPulsar(BasePulsar):
    total_integration_hours = models.DecimalField(max_digits=12, decimal_places=1)
    last_sn_raw = models.DecimalField(max_digits=12, decimal_places=1)
    highest_sn_raw = models.DecimalField(max_digits=12, decimal_places=1)
    lowest_sn_raw = models.DecimalField(max_digits=12, decimal_places=1)
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
        total_integration_hours = sum(
            folding.processing.observation.duration
            for folding in foldings
            if folding.processing.observation.duration
        ) / 60 / 60

        last_sn_raw = results.get('snr', 0)
        last_integration_minutes = latest_folding_observation.processing.observation.duration / 60

        all_projects = ", ".join({observation.project.short for observation in folding_observations})

        # Generate a list of different projects and how many observations belong to them.
        # Then find the one with the highest count.
        most_common_project = max(Counter([observation.project.short for observation in folding_observations]))

        highest_sn_raw = max(folding.processing.results.get('snr', 1) for folding in foldings)
        lowest_sn_raw = min(folding.processing.results.get('snr', 0) for folding in foldings)

        bands = ", ".join({
            cls.get_band(observation.instrument_config.frequency) for observation in folding_observations
        })

        return FoldPulsar.objects.update_or_create(
            main_project=program_name,
            jname=pulsar.jname,
            defaults={
                "all_projects": all_projects,
                "project": most_common_project,
                "band": bands,
                "latest_observation": latest_observation,
                "first_observation": first_observation,
                "timespan": timespan,
                "number_of_observations": number_of_observations,
                "total_integration_hours": total_integration_hours,
                "last_sn_raw": last_sn_raw,
                "highest_sn_raw": highest_sn_raw or 0,
                "lowest_sn_raw": lowest_sn_raw or 0,
                "last_integration_minutes": last_integration_minutes or 0,
                "avg_sn_pipe": cls.get_average_snr_over_5min(folding_observations),
                "max_sn_pipe": cls.get_max_snr_over_5min(folding_observations),
                "beam": latest_folding_observation.processing.observation.instrument_config.beam,
                "comment": pulsar.comment
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

        return max((o['snr'] / math.sqrt(o['length']) * sqrt_300) for o in observation_results)


class FoldDetailImage(models.Model):
    fold_pulsar_detail = models.ForeignKey("FoldPulsarDetail", related_name='images', on_delete=models.CASCADE)
    image_type = models.CharField(max_length=64, null=True)
    url = models.URLField()

    @property
    def plot_type(self):
        return self.image_type.split('.')[-2]

    @property
    def generic_plot_type(self):
        return next((key for key, values in PLOT_NAMES.items() if self.plot_type in values), self.plot_type)

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
    utc = models.DateTimeField()  # start time
    project = models.CharField(max_length=50)
    embargo_end_date = models.DateTimeField(null=True)
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
    dm_meerpipe = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    rm_meerpipe = models.DecimalField(max_digits=12, decimal_places=4, null=True)
    sn_backend = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    sn_meerpipe = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    flux = models.DecimalField(max_digits=12, decimal_places=6, null=True)
    ra = models.CharField(max_length=16, null=True)
    dec = models.CharField(max_length=16, null=True)
    tsubint = models.DecimalField(max_digits=12, decimal_places=1, null=True)
    schedule = models.CharField(max_length=16, null=True)
    phaseup = models.CharField(max_length=16, null=True)
    frequency = models.DecimalField(null=True, max_digits=15, decimal_places=9)
    npol = models.IntegerField(null=True)
    ephemeris_download_link = models.URLField(null=True)
    toas_download_link = models.URLField(null=True)

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
    def get_sn_meerpipe(cls, folding, pipeline_name):
        try:
            return folding.processing.processings_set.get(pipeline__name=pipeline_name).results.get('snr', None)
        except Processings.DoesNotExist:
            return None

    @classmethod
    def get_ephemeris_link(cls, pulsar):
        # ex: 'https://pulsars.org.au/media/MeerKAT/MeerPIPE_TPA/J1909-3744/2022-08-29-19:03:27/3/J1909-3744.par

        foldings = Foldings.objects.filter(
            folding_ephemeris__pulsar=pulsar
        )

        for folding in foldings:
            pipeline_files = Pipelinefiles.objects.filter(processing__parent=folding.processing)
            for pipleline_file in pipeline_files:
                if str(pipleline_file.file).endswith(f'{pulsar.jname}.par'):
                    return str(pipleline_file.file)

        return ''

    @classmethod
    def get_toas_link(cls, pulsar):
        # ex: 'https://pulsars.org.au/media/MeerKAT/MeerPIPE_PTA/J1843-1448/2022-08-29-18:20:32/3/pta.J1843-1448_global.tim.gz'

        foldings = Foldings.objects.filter(
            folding_ephemeris__pulsar=pulsar
        )

        for folding in foldings:
            pipeline_files = Pipelinefiles.objects.filter(processing__parent=folding.processing)
            for pipleline_file in pipeline_files:
                if str(pipleline_file.file).endswith(f'{pulsar.jname}_global.tim.gz'):
                    return str(pipleline_file.file)

        return ''

    @classmethod
    def get_flux(cls, folding, pipeline_name):
        """Get the flux value for a folding observation."""
        # The order to try projects as set by the science team.

        # ToDo: Implement molonglo flux data
        # Molonglo pipeline name is MONSPSR_CLEAN?
        # if pipeline_name == 'MONSPSR_CLEAN':
        #    return folding.processing.processings_set.last().results.get('flux', None)

        project_priority = ['MeerPIPE_PTA', 'MeerPIPE_TPA', 'MeerPIPE_RelBin']
        # Remove the actual folding observation project because we try that first.

        project_priority_order = [project for project in project_priority if project is not pipeline_name]

        try:
            # We want the flux value set to the real project if there is one.
            flux = folding.processing.processings_set.get(pipeline__name=pipeline_name).results.get('flux', None)

            if flux is not None:
                return flux

            # Its better to have a value from another project than no value at all.
            for project in project_priority_order:
                flux = folding.processing.processings_set.get(pipeline__name=project).results.get('flux', None)
                if flux is not None:
                    return flux

        except Processings.DoesNotExist:
            return None

    @classmethod
    def update_or_create(cls, folding):
        pulsar = folding.folding_ephemeris.pulsar
        observation = folding.processing.observation

        try:
            main_project = observation.project.program.name
            fold_pulsar = FoldPulsar.objects.get(jname=pulsar.jname, main_project=main_project)
        except FoldPulsar.DoesNotExist:
            print("FoldPulsar ", pulsar.jname, main_project, " does not exist")
            return
        except AttributeError:
            # If an observation doesn't have a project or program we want to skip it.
            # Hopefully this never happens.
            return

        # Calculate and set the embargo end date from observation and main project.
        # At this stage, we use the observation utc_start and main_project's embargo_period to do the calculation,
        # later we will apply the processing.embargo_end as well.
        embargo_end_date = observation.utc_start + observation.project.embargo_period

        results = folding.processing.results or {}
        pipeline_name = f"MeerPIPE_{observation.project.short}"
        sn_meerpipe = cls.get_sn_meerpipe(folding, pipeline_name)
        flux = cls.get_flux(folding, pipeline_name)

        new_fold_pulsar_detail, created = FoldPulsarDetail.objects.update_or_create(
            fold_pulsar=fold_pulsar,
            utc=observation.utc_start,
            defaults={
                "project": observation.project.short,
                "embargo_end_date": embargo_end_date,
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
                "dm_meerpipe": folding.folding_ephemeris.dm,
                "rm_meerpipe": folding.folding_ephemeris.rm,
                "sn_backend": results.get('snr', None),
                "flux": flux,
                "sn_meerpipe": sn_meerpipe,
                "schedule": "12",
                "phaseup": "12",
                "frequency": observation.instrument_config.frequency,
                "npol": folding.npol,
                "ephemeris_download_link": cls.get_ephemeris_link(pulsar=pulsar),
                "toas_download_link": cls.get_toas_link(pulsar=pulsar),
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
    embargo_end_date = models.DateTimeField(null=True)
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
    dm = models.DecimalField(max_digits=12, decimal_places=4)
    tsamp = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-utc"]

    @classmethod
    def update_or_create(cls, filter_bankings):
        observation = filter_bankings.processing.observation
        searchmode_pulsar = SearchmodePulsar.objects.get(jname=observation.target.name)

        # calculate and set the embargo end date from observation and main project(observation.project??).
        # at this stage, we use the observation utc_start and main_project's embargo_period to do the calculation
        # later we will apply the processing.embargo_end as well
        embargo_end_date = observation.utc_start + observation.project.embargo_period

        return cls.objects.update_or_create(
            searchmode_pulsar=searchmode_pulsar,
            utc=filter_bankings.processing.observation.utc_start,
            defaults={
                "project": observation.project.short,
                "embargo_end_date": embargo_end_date,
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

        total_integration = sum(session.integrations for session in session_pulsars)

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
    flux_hi = models.URLField(null=True)
    flux_lo = models.URLField(null=True)
    phase_vs_frequency_hi = models.URLField(null=True)
    phase_vs_frequency_lo = models.URLField(null=True)
    phase_vs_time_hi = models.URLField(null=True)
    phase_vs_time_lo = models.URLField(null=True)

    class Meta:
        ordering = ["-session_display__start"]

    @property
    def jname(self):
        return self.fold_pulsar.jname

    @property
    def pulsar_type(self):
        return 'search' if self.search_pulsar else 'fold'

    @classmethod
    def get_session_image(cls, images, plot_type, resolution="hi"):
        # Make sure there are images to process.
        if images is None:
            return None

        # Try and find a cleaned image favouring this order: relbin, tpa, pta.
        # Skip if it's a bad plot type by setting [] as the default.
        for name in PLOT_NAMES.get(plot_type, []):
            if images.filter(image_type=f"relbin.{name}.{resolution}").exists():
                return images.get(image_type=f"relbin.{name}.{resolution}").url

            if images.filter(image_type=f"tpa.{name}.{resolution}").exists():
                return images.get(image_type=f"tpa.{name}.{resolution}").url

            if images.filter(image_type=f"pta.{name}.{resolution}").exists():
                return images.get(image_type=f"pta.{name}.{resolution}").url

        # If there's no cleaned image try and get a raw image.
        try:
            return images.get(image_type=f"{plot_type}.{resolution}").url
        except FoldDetailImage.DoesNotExist:
            return None

    @classmethod
    def update_or_create(cls, session, pulsar):
        if isinstance(pulsar, SearchmodePulsar):
            last_observation = pulsar.searchmodepulsardetail_set.filter(utc__range=(session.start, session.end)).last()
            images = None
            fold_pulsar = None
            search_pulsar = pulsar
        elif isinstance(pulsar, FoldPulsar):
            last_observation = pulsar.foldpulsardetail_set.filter(utc__range=(session.start, session.end)).last()
            images = last_observation.images.all()
            fold_pulsar = pulsar
            search_pulsar = None
        else:
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
                "flux_hi": cls.get_session_image(images, 'flux'),
                "flux_lo": cls.get_session_image(images, 'flux'),
                "phase_vs_frequency_hi": cls.get_session_image(images, 'freq'),
                "phase_vs_frequency_lo": cls.get_session_image(images, 'freq'),
                "phase_vs_time_hi": cls.get_session_image(images, 'time'),
                "phase_vs_time_lo": cls.get_session_image(images, 'time'),
            },
        )
