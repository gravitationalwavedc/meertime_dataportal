import pytest
from datetime import datetime
from .storage import get_upload_location
from .models import Pipelineimages, Processings, Observations, Instrumentconfigs, Targets

from model_bakery import baker


def test_get_upload_location():
    expected = "J0437-4715/2020-10-10-10:10:10/4/uploaded.dat"

    pipelineimage = baker.prepare(
        "dataportal.Pipelineimages",
        image_type="uploaded.dat",
        processing__observation__target__name="J0437-4715",
        processing__observation__instrument_config__beam=4,
        processing__observation__utc_start=datetime.strptime("2020-10-10-10:10:10", "%Y-%m-%d-%H:%M:%S"),
    )

    assert get_upload_location(pipelineimage, "uploaded.dat") == expected
