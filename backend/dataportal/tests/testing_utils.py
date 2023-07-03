import os
import json
from datetime import datetime

from django.core.files.base import ContentFile

from utils.ephemeris import parse_ephemeris_file
from dataportal.storage import create_file_hash
from dataportal.models import (
    Pulsar,
    Telescope,
    MainProject,
    Project,
    Ephemeris,
    Template,
    Calibration,
    Observation,
    PipelineRun,
    PulsarFoldResult,
    PulsarFoldSummary,
    # PipelineImage,
    PipelineFile,
    Toa,
    Residual,
)

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


def create_basic_data():
    pulsar = Pulsar.objects.create(name="J0125-2327")

    telescope = Telescope.objects.create(name="my first telescope")

    main_project = MainProject.objects.create(name="MeerTime", telescope=telescope)

    project = Project.objects.create(code="SCI_thinga_MB", short="RelBin", main_project=main_project)

    with open(os.path.join(TEST_DATA_DIR, "J0125-2327.par"), 'r') as par_file:
        par_text = par_file.read()
    ephemeris_dict = parse_ephemeris_file(par_text)
    ephemeris, created = Ephemeris.objects.get_or_create(
        pulsar=pulsar,
        project=project,
        # TODO add created_by
        ephemeris_data=json.dumps(ephemeris_dict),
        p0=ephemeris_dict["P0"],
        dm=ephemeris_dict["DM"],
        valid_from=ephemeris_dict["START"],
        valid_to=ephemeris_dict["FINISH"],
    )

    with open(os.path.join(TEST_DATA_DIR, "J0125-2327.std"), 'rb') as template_file:
        file_content = template_file.read()
        template = Template.objects.create(
            pulsar=pulsar,
            project=project,
            band="LBAND",
            template_hash=create_file_hash(ContentFile(file_content)),
        )
        # template.save()
        template.template_file.save(template_file.name, ContentFile(file_content), save=True)

    return pulsar, telescope, project, ephemeris, template


def create_observation(json_path, pulsar, telescope, project, ephemeris):
    # Load data from json
    with open(json_path, 'r') as json_file:
        meertime_data = json.load(json_file)

    # Get or upload calibration
    calibration = Calibration.objects.create(
        delay_cal_id=meertime_data["delaycal_id"],
        phase_up_id=meertime_data["phaseup_id"],
        calibration_type=meertime_data["cal_type"],
        location=meertime_data["cal_location"],
    )

    utc_start_dt = datetime.strptime(f"{meertime_data['utcStart']} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc_start_dt = utc_start_dt.strftime("%Y-%m-%dT%H:%M:%S+0000")
    observation = Observation.objects.create(
        pulsar=pulsar,
        telescope=telescope,
        project=project,
        calibration=calibration,
        ephemeris=ephemeris,
        utc_start=utc_start_dt,
        frequency=meertime_data["frequency"],
        bandwidth=meertime_data["bandwidth"],
        nchan=meertime_data["nchan"],
        beam=meertime_data["beam"],
        nant=meertime_data["nant"],
        nant_eff=meertime_data["nantEff"],
        npol=meertime_data["npol"],
        obs_type=meertime_data["obsType"],
        raj=meertime_data["raj"],
        decj=meertime_data["decj"],
        duration=meertime_data["duration"],
        nbit=meertime_data["nbit"],
        tsamp=meertime_data["tsamp"],
        fold_nbin=meertime_data["foldNbin"],
        fold_nchan=meertime_data["foldNchan"],
        fold_tsubint=meertime_data["foldTsubint"],
        filterbank_nbit=meertime_data["filterbankNbit"],
        filterbank_npol=meertime_data["filterbankNpol"],
        filterbank_nchan=meertime_data["filterbankNchan"],
        filterbank_tsamp=meertime_data["filterbankTsamp"],
        filterbank_dm=meertime_data["filterbankDm"],
    )

    return observation


def create_pulsar_with_observations():
    pulsar, telescope, project, ephemeris, template = create_basic_data()

    obs1 = create_observation(os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"), pulsar, telescope, project, ephemeris)
    obs2 = create_observation(os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"), pulsar, telescope, project, ephemeris)

    pipeline_run1 = PipelineRun.objects.create(
        observation=obs1,
        ephemeris=ephemeris,
        template=template,
        pipeline_name = "meerpipe",
        pipeline_description = "MeerTime pipeline",
        pipeline_version = "3.0.0",
        created_by = "test",
        job_state = "done",
        location = "/test/location",
        dm=20.,
        # dm_err   = models.FloatField(null=True)
        # dm_epoch = models.FloatField(null=True)
        # dm_chi2r = models.FloatField(null=True)
        # dm_tres  = models.FloatField(null=True)
        sn=100.0,
        flux=25.,
        rm=10.,
        # percent_rfi_zapped = models.FloatField(null=True)
    )
    pipeline_run2 = PipelineRun.objects.create(
        observation=obs2,
        ephemeris=ephemeris,
        template=template,
        pipeline_name = "meerpipe",
        pipeline_description = "MeerTime pipeline",
        pipeline_version = "3.0.0",
        created_by = "test",
        job_state = "done",
        location = "/test/location",
        dm=20.1,
        # dm_err   = models.FloatField(null=True)
        # dm_epoch = models.FloatField(null=True)
        # dm_chi2r = models.FloatField(null=True)
        # dm_tres  = models.FloatField(null=True)
        sn=50.0,
        flux=25.1,
        rm=10.1,
        # flux = models.FloatField(null=True)
        # rm = models.FloatField(null=True)
        # percent_rfi_zapped = models.FloatField(null=True)
    )

    return

