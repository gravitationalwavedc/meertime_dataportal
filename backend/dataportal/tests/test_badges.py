
import os
import pytest

from dataportal.models import (
    PipelineRun,
    Badge,
)

from dataportal.tests.testing_utils import setup_query_test, create_basic_data, create_observation_pipeline_run_toa

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_rfi_badge():
    client, user, telescope, project, ephemeris, template, pipeline_run, observation, cal = setup_query_test()

    # Create RFI badge
    rfi_badge, created = Badge.objects.get_or_create(
        name="Strong RFI",
        description="Over 20% of RFI removed from observation",
    )

    # PipelineRun created in setup_query_test has 10% Rfi so should not have an RFI badge
    assert pipeline_run.percent_rfi_zapped < 0.2
    assert rfi_badge not in pipeline_run.badges.all()

    # Make a PipelineRun with 30% Rfi so should have an RFI badge
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
        dm=20.0,
        dm_err=1.0,
        dm_epoch=1.0,
        dm_chi2r=1.0,
        dm_tres=1.0,
        sn=100.0,
        flux=25.0,
        rm=10.0,
        rm_err=1.0,
        percent_rfi_zapped=0.3,
    )
    assert pipeline_run.percent_rfi_zapped > 0.2
    assert rfi_badge in pipeline_run.badges.all()


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_rm_badge():
    telescope, project, ephemeris, template = create_basic_data()

    # Create RM badge
    rm_badge, created = Badge.objects.get_or_create(
        name="RM Drift",
        description="The Rotation Measure has drifted three weighted standard deviations from the weighted mean",
    )

    # Create five Pipeline runs with one RM values over 3 STD away from the mean
    _, _, pr1 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"),
        telescope,
        template,
        rm=10.0,
        rm_err=0.1,
    )
    _, _, pr2 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"),
        telescope,
        template,
        rm=10.1,
        rm_err=0.1,
    )
    _, _, pr3 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
        telescope,
        template,
        rm=10.2,
        rm_err=0.1,
    )
    # Check no badges at this point
    assert pr1.badges.filter(id=rm_badge.id).count() == 0
    assert pr2.badges.filter(id=rm_badge.id).count() == 0
    assert pr3.badges.filter(id=rm_badge.id).count() == 0
    _, _, pr4 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-12-15-17:22:31_1_J0125-2327.json"),
        telescope,
        template,
        rm=200.0,
        rm_err=10,
    )
    _, _, pr5 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-12-15-17:22:31_1_J0125-2327.json"),
        telescope,
        template,
        rm=10.3,
        rm_err=0.1,
    )
    # And one with a None RM
    _, _, pr6 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-12-15-17:22:31_1_J0125-2327.json"),
        telescope,
        template,
        rm=None,
        rm_err=None,
    )
    # Test only the last obs has the badge
    assert pr1.badges.filter(id=rm_badge.id).count() == 0
    assert pr2.badges.filter(id=rm_badge.id).count() == 0
    assert pr3.badges.filter(id=rm_badge.id).count() == 0
    assert pr4.badges.filter(id=rm_badge.id).count() == 1
    assert pr5.badges.filter(id=rm_badge.id).count() == 0
    assert pr6.badges.filter(id=rm_badge.id).count() == 0


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_dm_badge():
    telescope, project, ephemeris, template = create_basic_data()
    dm_badge, created = Badge.objects.get_or_create(
        name="Dm Drift",
        description="The DM has drifted away from the median DM of the pulsar enough to cause a dispersion of one",
    )

    # Create for three pipeline runs where one is over 0.001 DM away from the median which will be more than 1 bin
    _, _, pr1 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"),
        telescope,
        template,
        dm=10.000,
    )
    _, _, pr2 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"),
        telescope,
        template,
        dm=10.0005,
    )
    _, _, pr3 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
        telescope,
        template,
        dm=11.002,
    )
    # And one with a None DM
    _, _, pr4 = create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
        telescope,
        template,
        dm=None,
    )
    # Test only last pr has badge
    assert pr1.badges.filter(id=dm_badge.id).count() == 0
    assert pr2.badges.filter(id=dm_badge.id).count() == 0
    assert pr3.badges.filter(id=dm_badge.id).count() == 1
    assert pr4.badges.filter(id=dm_badge.id).count() == 0
