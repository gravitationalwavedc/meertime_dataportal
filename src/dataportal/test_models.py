import pytest
import random
import string
from datetime import datetime, timedelta

from .models import (
    Ephemerides,
    Filterbankings,
    Foldings,
    Instrumentconfigs,
    Observations,
    Pipelines,
    Pulsars,
    Pulsartargets,
    Processings,
    Projects,
    Targets,
    Telescopes,
)


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


@pytest.mark.django_db
def test_foldings_band():
    utc_later_str = "2000-01-01-12:59:12"
    utc_earlier_str = "1999-01-01-12:59:12"
    _, _ = generate_two_db_entries("J1234-5678", utc_later_str, utc_earlier_str)
    folding = Foldings.objects.all().first()
    assert folding.band == "L-band"


default_entry_config = {
    "raj": "04:37:00.000",
    "decj": "-47:15:00.000",
    "name": "foo",
    "bandwidth": 256.0,
    "frequency": 1421.0,
    "nchan": 4096,
    "nbin": 1024,
    "npol": 2,
    "beam": 2,
    "p0": 4.3,
    "dm": 2.77,
    "rm": 0.0,
    "duration": 100.0,
    "nant": 64,
    "nant_eff": 64,
    "nbit": 8,
    "tsamp": 0.000064,
    "proposal": "SCI-MB",
    "proposal_short": "test",
    "telescope": "MK",
    "ephemeris": "",
    "pipeline_version": "A",
    "tsubint": 8.0,
}


def generate_db_entry(psr, utc, config=default_entry_config):
    """
    Helper method to populate the database with a test entry for a pulsar with name specified by psr and at the time of utc. Optionally, all parameters can be modifed by providing a entry config dictionary.

    Return the utc as datetime with timezone set
    """
    psr, _ = Pulsars.objects.get_or_create(jname=psr)
    target, _ = Targets.objects.get_or_create(name=psr, raj=config["raj"], decj=config["decj"])
    psrtarget, _ = Pulsartargets.objects.get_or_create(pulsar=psr, target=target)
    proposal, _ = Projects.objects.get_or_create(code=config["proposal"], short=config["proposal_short"])
    instrument = Instrumentconfigs.objects.create(
        name=config["name"],
        bandwidth=config["bandwidth"],
        frequency=config["frequency"],
        nchan=config["nchan"],
        npol=config["npol"],
        beam=config["beam"],
    )
    telescope = Telescopes.objects.create(name=config["telescope"])

    utc_dt = datetime.strptime(f"{utc} +0000", "%Y-%m-%d-%H:%M:%S %z")

    eph = Ephemerides.objects.create(
        pulsar=psr,
        created_at=utc_dt,
        created_by=config["name"],
        ephemeris=config["ephemeris"],
        p0=config["p0"],
        dm=config["dm"],
        rm=config["rm"],
        valid_from=utc_dt,
        valid_to=utc_dt,
    )
    pipeline = Pipelines.objects.create(
        name=config["name"], created_at=utc_dt, revision=config["pipeline_version"], created_by=config["name"]
    )

    obs = Observations.objects.create(
        target=target,
        telescope=telescope,
        instrument_config=instrument,
        project=proposal,
        utc_start=utc_dt,
        duration=config["duration"],
        nant=config["nant"],
        nant_eff=config["nant_eff"],
    )

    proc = Processings.objects.create(observation=obs, pipeline=pipeline, embargo_end=utc_dt)
    Foldings.objects.create(
        processing=proc,
        folding_ephemeris=eph,
        nbin=config["nbin"],
        npol=config["npol"],
        nchan=config["nchan"],
        dm=config["dm"],
        tsubint=config["tsubint"],
    )
    Filterbankings.objects.create(
        processing=proc,
        nbit=config["nbit"],
        npol=config["npol"],
        nchan=config["nchan"],
        tsamp=config["tsamp"],
        dm=config["dm"],
    )
    return utc_dt


def generate_two_db_entries(psr, utc_later_str, utc_earlier_str):
    utc_later_dt = generate_db_entry(psr, utc_later_str)
    utc_earlier_dt = generate_db_entry(psr, utc_earlier_str)

    return utc_earlier_dt, utc_later_dt


@pytest.mark.django_db
def test_get_latest_observations():
    expected_psr = "J1234-5678"
    utc_later_str = "2000-01-01-12:59:12"
    utc_earlier_str = "1999-01-01-12:59:12"

    expected_utc_earlier, expected_utc_later = generate_two_db_entries(expected_psr, utc_later_str, utc_earlier_str)

    obs = Pulsars.get_latest_observations()

    assert obs[0]["jname"] == expected_psr
    assert obs[0]["first"] == expected_utc_earlier
    assert obs[0]["last"] == expected_utc_later
    assert obs[0]["nobs"] == 2


@pytest.mark.django_db
def test_get_observations_for_pulsar():
    expected_psr = "J1234-5678"
    utc_later_str = "2000-01-01-12:59:12"
    utc_earlier_str = "1999-01-01-12:59:12"

    expected_utc_earlier, expected_utc_later = generate_two_db_entries(expected_psr, utc_later_str, utc_earlier_str)

    obs_detail = Pulsars.objects.all().first().get_observations_for_pulsar()
    first = obs_detail.first()
    last = obs_detail.last()

    assert first.utc == expected_utc_later
    assert last.utc == expected_utc_earlier


@pytest.mark.django_db
def test_get_observation_details():
    utc = "2000-01-01-12:59:12"

    utc_dt = generate_db_entry("J0437-4715", utc)
    psr = Pulsars.objects.get(jname="J0437-4715")

    obs = Foldings.get_observation_details(psr, utc_dt, default_entry_config["beam"])

    assert obs.jname == psr.jname
    assert obs.utc == utc_dt
    assert obs.beam == str(default_entry_config["beam"])
    assert obs.proposal == default_entry_config["proposal"]
    assert obs.frequency == default_entry_config["frequency"]
    assert obs.bw == default_entry_config["bandwidth"]
    assert obs.ra == default_entry_config["raj"]
    assert obs.dec == default_entry_config["decj"]
    assert obs.duration == default_entry_config["duration"]
    assert obs.nant == default_entry_config["nant"]
    assert obs.nant_eff == default_entry_config["nant_eff"]
