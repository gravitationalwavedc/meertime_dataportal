import pytest
import random
import string
from datetime import datetime, timedelta

from .models import Observations, Searchmode, Fluxcal, Pulsars, Utcs, Proposals


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
    proposal = Proposals.objects.create(proposal="SCI_MB", proposal_short="test")
    utc_later_dt = datetime.strptime(f"{utc_later_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc_later = Utcs.objects.create(utc_ts=utc_later_dt)

    utc_earlier_dt = datetime.strptime(f"{utc_earlier_str} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc_earlier = Utcs.objects.create(utc_ts=utc_earlier_dt)

    Observations.objects.create(pulsar=psr, utc=utc_later, beam=expected_beam, proposal=proposal)
    Observations.objects.create(pulsar=psr, utc=utc_earlier, beam=expected_beam, proposal=proposal)
    Searchmode.objects.create(pulsar=psr, utc=utc_later, beam=expected_beam, proposal=proposal)
    Searchmode.objects.create(pulsar=psr, utc=utc_earlier, beam=expected_beam, proposal=proposal)
    Fluxcal.objects.create(pulsar=psr, utc=utc_later, beam=expected_beam, proposal=proposal)
    Fluxcal.objects.create(pulsar=psr, utc=utc_earlier, beam=expected_beam, proposal=proposal)

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


@pytest.mark.django_db
def test_get_last_session_by_gap():
    # this test will create 9 observations
    # 7 of them with a gap of a minute between the end of one and start of the next one
    # and one with a gap of 3 hours and one with gap of a day
    # we start with the last obs and go backwards in time
    n_subsequent_obs = 7
    length = 60.0
    small_gap = 60.0
    big_gap_hours = 3.0

    beam = 1
    psr = Pulsars.objects.create(jname="J1234-5678")
    utc_start = "2000-01-01-12:59:12"
    utc_start_dt = datetime.strptime(f"{utc_start} +0000", "%Y-%m-%d-%H:%M:%S %z")

    # this is needed to get through the default proposal filter
    proposal = Proposals.objects.create(proposal="SCI-MB", proposal_short="test")

    for iobs in range(n_subsequent_obs):
        # add the gap
        utc_start_dt -= timedelta(seconds=small_gap)

        utc = Utcs.objects.create(utc_ts=utc_start_dt)
        obs = Observations.objects.create(pulsar=psr, utc=utc, beam=beam, length=length, proposal=proposal)
        # calculate the end of the observation and set it as the starting point for the next obs
        utc_start_dt -= timedelta(seconds=length + small_gap)

    # now add the observation with a longer gap
    utc_start_dt -= timedelta(seconds=big_gap_hours * 3600.0)
    utc = Utcs.objects.create(utc_ts=utc_start_dt)
    obs = Observations.objects.create(pulsar=psr, utc=utc, beam=beam, length=length, proposal=proposal)

    # now add the observation a day earlier
    utc_start_dt -= timedelta(days=1)
    utc = Utcs.objects.create(utc_ts=utc_start_dt)
    obs = Observations.objects.create(pulsar=psr, utc=utc, beam=beam, length=length, proposal=proposal)

    # here we should find n_subsequent_obs
    count_default = Observations.get_last_session_by_gap().count()
    # here we should find n_subsequent_obs plus the one after a larger gap
    count_gt_big_gap = Observations.get_last_session_by_gap(max_gap=(big_gap_hours + 1.0) * 3600.0).count()
    # here we should only find one obs
    count_lt_small_gap = Observations.get_last_session_by_gap(max_gap=small_gap / 6).count()

    assert count_default == n_subsequent_obs
    assert count_gt_big_gap == n_subsequent_obs + 1
    assert count_lt_small_gap == 1
