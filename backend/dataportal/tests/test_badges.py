
import os
import pytest

from dataportal.models import (
    PipelineRun,
    Badge,
)

from dataportal.tests.testing_utils import setup_query_test

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
