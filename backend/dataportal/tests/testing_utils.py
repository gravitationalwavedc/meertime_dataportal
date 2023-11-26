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
    Toa,
    Residual,
)

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
CYPRESS_FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/cypress/fixtures")


def create_basic_data():
    telescope = Telescope.objects.create(name="my first telescope")

    pulsar = Pulsar.objects.create(
        name="J0125-2327",
        comment="PSR J0125-2327 is a millisecond pulsar with a period of 3.68 milliseconds and has a small dispersion measure of 9.597 pc/cm^3. It is a moderately bright pulsar with a 1400 MHz catalogue flux density of 2.490 mJy. PSR J0125-2327 is a Southern Hemisphere pulsar. PSR J0125-2327 has no measured period derivative. The estimated distance to J0125-2327 is 873 pc. This pulsar appears to be solitary.",
    )

    main_project = MainProject.objects.create(name="MeerTIME", telescope=telescope)

    project = Project.objects.create(code="SCI-20180516-MB-05", short="PTA", main_project=main_project)
    project = Project.objects.create(code="SCI-20180516-MB-02", short="TPA", main_project=main_project)
    project = Project.objects.create(code="SCI-20180516-MB-04", short="GC", main_project=main_project)

    project = Project.objects.create(code="SCI_thinga_MB", short="RelBin", main_project=main_project)

    with open(os.path.join(TEST_DATA_DIR, "J0125-2327.par"), 'r') as par_file:
        par_text = par_file.read()
    ephemeris_dict = parse_ephemeris_file(par_text)
    ephemeris, _ = Ephemeris.objects.get_or_create(
        pulsar=pulsar,
        project=project,
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

    return telescope, project, ephemeris, template


def create_observation(json_path, telescope):
    # Load data from json
    with open(json_path, 'r') as json_file:
        meertime_data = json.load(json_file)

    # Get or upload calibration
    calibration = Calibration.objects.create(
        schedule_block_id=meertime_data["schedule_block_id"],
        calibration_type=meertime_data["cal_type"],
        location=meertime_data["cal_location"],
    )
    print(calibration.id)

    pulsar, _ = Pulsar.objects.get_or_create(
        name=meertime_data["pulsarName"],
        comment="PSR J0125-2327 is a millisecond pulsar with a period of 3.68 milliseconds and has a small dispersion measure of 9.597 pc/cm^3. It is a moderately bright pulsar with a 1400 MHz catalogue flux density of 2.490 mJy. PSR J0125-2327 is a Southern Hemisphere pulsar. PSR J0125-2327 has no measured period derivative. The estimated distance to J0125-2327 is 873 pc. This pulsar appears to be solitary.",
    )

    project = Project.objects.get(code=meertime_data["projectCode"])

    if meertime_data["ephemerisText"] == "":
        ephemeris = None
    else:
        ephemeris_dict = parse_ephemeris_file(meertime_data["ephemerisText"])
        ephemeris, _ = Ephemeris.objects.get_or_create(
            pulsar=pulsar,
            project=project,
            ephemeris_data=json.dumps(ephemeris_dict),
            p0=ephemeris_dict["P0"],
            dm=ephemeris_dict["DM"],
            valid_from=ephemeris_dict["START"],
            valid_to=ephemeris_dict["FINISH"],
        )

    utc_start_dt = datetime.strptime(f"{meertime_data['utcStart']} +0000", "%Y-%m-%d-%H:%M:%S %z")
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

    return observation, calibration

def create_pipeline_run(obs, ephemeris, template):
    pipeline_run = PipelineRun.objects.create(
        observation=obs,
        ephemeris=ephemeris,
        template=template,
        pipeline_name = "meerpipe",
        pipeline_description = "MeerTime pipeline",
        pipeline_version = "3.0.0",
        created_by = "test",
        job_state = "done",
        location = "/test/location",
        dm=20.,
        dm_err=1.,
        dm_epoch=1.,
        dm_chi2r=1.,
        dm_tres=1.,
        sn=100.0,
        flux=25.,
        rm=10.,
        rm_err=1.,
        percent_rfi_zapped=10,
    )
    return pipeline_run


def create_pulsar_with_observations():
    telescope, project, ephemeris, template = create_basic_data()

    # Search
    obs1, cal1 = create_observation(os.path.join(TEST_DATA_DIR, "J1614+0737_2023-08-01-18:21:59.json"), telescope)
    obs2, cal2 = create_observation(os.path.join(TEST_DATA_DIR, "J1709-3626_2020-03-15-22:58:52.json"), telescope)
    obs3, cal3 = create_observation(os.path.join(TEST_DATA_DIR, "OmegaCen1_2023-06-27-11:37:31.json"), telescope)

    # Fold
    obs4, cal4 = create_observation(os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"), telescope)
    obs5, cal5 = create_observation(os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"), telescope)
    obs6, cal6 = create_observation(os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"), telescope)

    pipeline_run1 = create_pipeline_run(obs4, ephemeris, template)
    pipeline_run2 = create_pipeline_run(obs5, ephemeris, template)
    pipeline_run3 = create_pipeline_run(obs6, ephemeris, template)

    return telescope, project, ephemeris, template, pipeline_run1, obs4, cal4


def create_toas_and_residuals(
        observation,
        project,
        ephemeris,
        pipeline_run,
        template,
    ):
    residual = Residual.objects.create(
        mjd=1,
        day_of_year=1,
        residual_sec=2,
        residual_sec_err=3,
        residual_phase=4,
        residual_phase_err=5,
    )
    toa = Toa.objects.create(
        pipeline_run=pipeline_run,
        observation=observation,
        project=project,
        ephemeris=ephemeris,
        template=template,
        residual=residual,
        freq_MHz=6,
        mjd=7,
        mjd_err=8,
        length=9,
        dm_corrected=False,
        minimum_nsubs=True,
        obs_nchan=1,
    )
    return