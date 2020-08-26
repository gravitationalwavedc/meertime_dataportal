import pytest
import random
import string
from datetime import datetime

from .models import Observations, Searchmode, Fluxcal, Pulsars, Utcs


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def test_observation_band():
    observation = Observations(frequency=1238.128383)
    assert observation.band == "L-band"


def test_searchmode_band():
    search_mode = Searchmode(frequency=843)
    assert search_mode.band == "UHF"


def test_fluxcal_band():
    fluxcal = Fluxcal(frequency=1300.0)
    assert fluxcal.band == "L-band"


def generate_two_db_entries(_psr, utc_later_str, utc_earlier_str):
    expected_beam = 2
    psr = Pulsars.objects.create(jname=_psr)
    utc_later_dt = datetime.strptime(f"{utc_later_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc_later = Utcs.objects.create(utc=utc_later_str, utc_ts=utc_later_dt)

    utc_earlier_dt = datetime.strptime(f"{utc_earlier_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc_earlier = Utcs.objects.create(utc=utc_earlier_str, utc_ts=utc_earlier_dt)

    Observations.objects.create(pulsar=psr, utc=utc_later, beam=expected_beam)
    Observations.objects.create(pulsar=psr, utc=utc_earlier, beam=expected_beam)
    Searchmode.objects.create(pulsar=psr, utc=utc_later, beam=expected_beam)
    Searchmode.objects.create(pulsar=psr, utc=utc_earlier, beam=expected_beam)
    Fluxcal.objects.create(pulsar=psr, utc=utc_later, beam=expected_beam)
    Fluxcal.objects.create(pulsar=psr, utc=utc_earlier, beam=expected_beam)

    return utc_earlier_dt, utc_later_dt


@pytest.mark.django_db
def test_get_observations_no_project_id():
    expected_psr = "J1234-5678"
    utc_later_str = "2000-01-01-12:59:12"
    utc_earlier_str = "1999-01-01-12:59:12"

    expected_utc_earlier, expected_utc_later = generate_two_db_entries(expected_psr, utc_later_str, utc_earlier_str)

    obs = Pulsars.get_observations(mode="observations")
    search = Pulsars.get_observations(mode="searchmode")
    flux = Pulsars.get_observations(mode="fluxcal")
    fake = Pulsars.get_observations(mode=get_random_string(8))

    assert fake is None
    for tested_model in [obs, search, flux]:
        assert tested_model[0]["jname"] == expected_psr
        assert tested_model[0]["first"] == expected_utc_earlier
        assert tested_model[0]["last"] == expected_utc_later
        assert tested_model[0]["nobs"] == 2
