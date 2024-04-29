import json
import os
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from graphql_jwt.testcases import JSONWebTokenClient

from dataportal.models import (
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    PipelineRun,
    Project,
    Pulsar,
    Telescope,
    Template,
    Toa,
)
from dataportal.storage import create_file_hash
from utils.ephemeris import parse_ephemeris_file

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy", email="slayer@sunnydail.com")
    telescope, project, ephemeris, template, pipeline_run, obs, cal = create_pulsar_with_observations()
    return client, user, telescope, project, ephemeris, template, pipeline_run, obs, cal


def create_basic_data():
    telescope = Telescope.objects.create(name="my first telescope")

    pulsar = Pulsar.objects.create(
        name="J0125-2327",
        comment="PSR J0125-2327 is a millisecond pulsar with a period of 3.68 milliseconds and has a small dispersion measure of 9.597 pc/cm^3. It is a moderately bright pulsar with a 1400 MHz catalogue flux density of 2.490 mJy. PSR J0125-2327 is a Southern Hemisphere pulsar. PSR J0125-2327 has no measured period derivative. The estimated distance to J0125-2327 is 873 pc. This pulsar appears to be solitary.",  # noqa
    )

    # Meerkat
    main_project = MainProject.objects.create(name="MeerTIME", telescope=telescope)
    project = Project.objects.create(code="SCI-20180516-MB-05", short="PTA", main_project=main_project)
    project = Project.objects.create(code="SCI-20180516-MB-02", short="TPA", main_project=main_project)
    project = Project.objects.create(code="SCI-20180516-MB-04", short="GC", main_project=main_project)
    project = Project.objects.create(code="SCI_thinga_MB", short="RelBin", main_project=main_project)

    # Molonglo
    main_project = MainProject.objects.create(name="MONSPSR", telescope=telescope)
    project = Project.objects.create(code="MONSPSR_TIMING", short="MONSPSR_TIMING", main_project=main_project)

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

    with open(os.path.join(TEST_DATA_DIR, "J0125-2327.std"), "rb") as template_file:
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


def create_observation_pipeline_run_toa(json_path, telescope, template, make_toas=True, rm=10.0, rm_err=1.0, dm=20.0):
    # Load data from json
    with open(json_path, "r") as json_file:
        meertime_data = json.load(json_file)

    # Get or upload calibration
    calibration = Calibration.objects.create(
        schedule_block_id=meertime_data["schedule_block_id"],
        calibration_type=meertime_data["cal_type"],
        location=meertime_data["cal_location"],
    )

    pulsar, _ = Pulsar.objects.get_or_create(
        name=meertime_data["pulsarName"],
        comment="PSR J0125-2327 is a millisecond pulsar with a period of 3.68 milliseconds and has a small dispersion measure of 9.597 pc/cm^3. It is a moderately bright pulsar with a 1400 MHz catalogue flux density of 2.490 mJy. PSR J0125-2327 is a Southern Hemisphere pulsar. PSR J0125-2327 has no measured period derivative. The estimated distance to J0125-2327 is 873 pc. This pulsar appears to be solitary.",  # noqa
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

    if meertime_data["obsType"] == "fold":
        pipeline_run = PipelineRun.objects.create(
            observation=observation,
            ephemeris=ephemeris,
            template=template,
            pipeline_name="meerpipe",
            pipeline_description="MeerTime pipeline",
            pipeline_version="3.0.0",
            created_by="test",
            job_state="Completed",
            location="/test/location",
            dm=dm,
            dm_err=1.0,
            dm_epoch=1.0,
            dm_chi2r=1.0,
            dm_tres=1.0,
            sn=100.0,
            flux=25.0,
            rm=rm,
            rm_err=rm_err,
            percent_rfi_zapped=0.1,
        )
        if make_toas:
            Toa.objects.create(
                pipeline_run=pipeline_run,
                observation=observation,
                project=project,
                ephemeris=ephemeris,
                template=template,
                freq_MHz=6,
                mjd=7,
                mjd_err=8,
                length=9,
                dm_corrected=False,
                nsub_type="min",
                obs_nchan=1,
                day_of_year=1,
                residual_sec=2,
                residual_sec_err=3,
                residual_phase=4,
                residual_phase_err=5,
            )
    else:
        pipeline_run = None

    return observation, calibration, pipeline_run


def create_pulsar_with_observations():
    telescope, project, ephemeris, template = create_basic_data()

    # Search
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "J1614+0737_2023-08-01-18:21:59.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "J1709-3626_2020-03-15-22:58:52.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "OmegaCen1_2023-06-27-11:37:31.json"), telescope, template
    )

    # Fold
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"), telescope, template
    )
    obs, cal, pr = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"), telescope, template
    )

    return telescope, project, ephemeris, template, pr, obs, cal


def upload_toa_files(
    pipeline_run,
    project_short,
    nchan,
    template,
    toa_path,
    nsub_type="min",
):
    with open(toa_path, "r") as toa_file:
        toa_lines = toa_file.readlines()
        Toa.bulk_create(
            pipeline_run_id=pipeline_run.id,
            project_short=project_short,
            template_id=template.id,
            ephemeris_text=os.path.join(TEST_DATA_DIR, "J0125-2327.par"),
            toa_lines=toa_lines,
            dm_corrected=False,
            nsub_type=nsub_type,
            npol=1,
            nchan=nchan,
        )


def setup_timing_obs():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy", is_staff=True, is_superuser=True)
    telescope, _, _, template = create_basic_data()

    _, _, pr = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "timing_files/2023-10-22-04:41:07_1_J0437-4715.json"),
        telescope,
        template,
        make_toas=False,
    )
    # All files
    upload_toa_files(
        pr,
        "PTA",
        16,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim"),
    )
    upload_toa_files(
        pr,
        "PTA",
        1,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-22-04:41:07_zap.1ch1p1t.ar.tim"),
    )
    upload_toa_files(
        pr,
        "TPA",
        16,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim"),
    )
    upload_toa_files(
        pr,
        "TPA",
        1,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-22-04:41:07_zap.1ch1p1t.ar.tim"),
    )
    # Add last one twice to test duplicate detection
    upload_toa_files(
        pr,
        "TPA",
        1,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-22-04:41:07_zap.1ch1p1t.ar.tim"),
    )

    _, _, pr = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "timing_files/2023-10-30-02:18:35_1_J0437-4715.json"),
        telescope,
        template,
        make_toas=False,
    )
    upload_toa_files(
        pr,
        "PTA",
        16,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-30-02:18:35_zap.16ch1p1t.ar.tim"),
    )
    upload_toa_files(
        pr,
        "PTA",
        1,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-30-02:18:35_zap.1ch1p1t.ar.tim"),
    )
    upload_toa_files(
        pr,
        "TPA",
        16,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-30-02:18:35_zap.16ch1p1t.ar.tim"),
    )
    upload_toa_files(
        pr,
        "TPA",
        1,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-30-02:18:35_zap.1ch1p1t.ar.tim"),
    )
    # Add last one twice to test duplicate detection
    upload_toa_files(
        pr,
        "TPA",
        16,
        template,
        os.path.join(TEST_DATA_DIR, "timing_files/J0437-4715_2023-10-30-02:18:35_zap.16ch1p1t.ar.tim"),
    )

    return client, user
