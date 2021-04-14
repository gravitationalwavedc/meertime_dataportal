import pytest
from datetime import datetime
from .storage import get_upload_location
from .models import Observations, Pulsars, Utcs


def test_get_upload_location():
    expected = "J0437-4715/2020-10-10-10:10:10/4/uploaded.dat"

    psr = Pulsars(jname="J0437-4715")
    utc = Utcs(utc_ts=datetime.strptime("2020-10-10-10:10:10", "%Y-%m-%d-%H:%M:%S"))
    obs = Observations(pulsar=psr, beam=4, utc=utc)
    assert get_upload_location(obs, "uploaded.dat") == expected
