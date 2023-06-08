import pytest
from datetime import datetime
from .storage import get_upload_location, get_pipeline_upload_location
from .models import Pipelinefiles, Processings, Observations, Instrumentconfigs, Targets

from django.core.files import File
from unittest import mock
from model_bakery import baker

from .test_models import generate_db_entry, default_entry_config


def test_get_upload_location():
    expected = "MeerKAT/J0437-4715/2020-10-10-10:10:10/4/uploaded.dat"

    pipelineimage = baker.prepare(
        "dataportal.Pipelineimages",
        image_type="uploaded.dat",
        processing__observation__telescope__name="MeerKAT",
        processing__observation__target__name="J0437-4715",
        processing__observation__instrument_config__beam=4,
        processing__observation__utc_start=datetime.strptime("2020-10-10-10:10:10", "%Y-%m-%d-%H:%M:%S"),
    )

    assert get_upload_location(pipelineimage, "uploaded.dat") == expected


def test_get_pipeline_upload_location():
    expected = "MeerKAT/MeerPIPE_PTA/J0023+0923/2020-08-24-03:14:33/2/J0023+0923.par"

    pipelinefile = baker.prepare(
        "dataportal.Pipelinefiles",
        file_type="pta.parfile",
        processing__observation__telescope__name="MeerKAT",
        processing__pipeline__name="MeerPIPE_PTA",
        processing__observation__target__name="J0023+0923",
        processing__observation__instrument_config__beam=2,
        processing__observation__utc_start=datetime.strptime("2020-08-24-03:14:33", "%Y-%m-%d-%H:%M:%S"),
    )

    assert get_pipeline_upload_location(pipelinefile, "J0023+0923.par") == expected


@pytest.mark.django_db
def test_pipelinefiles_file_name_with_plus():
    update_config = {
        "name": "MeerPIPE_PTA",
        "telescope": "MeerKAT",
    }

    entry_config = default_entry_config.copy()
    entry_config.update(update_config)

    expected = "MeerKAT/MeerPIPE_PTA/J0023+0923/2020-08-24-03:14:33/2/J0023+0923.par"

    generate_db_entry(psr="J0023+0923", utc="2020-08-24-03:14:33", config=entry_config)
    processing = Processings.objects.first()
    mock_file = mock.MagicMock(spec=File)
    mock_file.name = "J0023+0923.par"

    pipelinefile = Pipelinefiles.objects.create(
        processing=processing,
        file=mock_file,
        file_type="pta.parfile",
    )

    assert pipelinefile.file.name == expected


@pytest.mark.django_db
def test_pipelinefiles_file_name_with_minus():
    update_config = {
        "name": "MeerPIPE_PTA",
        "telescope": "MeerKAT",
    }

    entry_config = default_entry_config.copy()
    entry_config.update(update_config)

    expected = "MeerKAT/MeerPIPE_PTA/J0023-0923/2020-08-24-03:14:33/2/J0023-0923.par"

    generate_db_entry(psr="J0023-0923", utc="2020-08-24-03:14:33", config=entry_config)
    processing = Processings.objects.first()
    mock_file = mock.MagicMock(spec=File)
    mock_file.name = "J0023-0923.par"

    pipelinefile = Pipelinefiles.objects.create(
        processing=processing,
        file=mock_file,
        file_type="pta.parfile",
    )

    assert pipelinefile.file.name == expected
