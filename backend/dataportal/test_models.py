import hashlib
import json
import pytest
import random
import string
import pytz
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.utils import IntegrityError

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
    Programs,
    Targets,
    Telescopes,
    Sessions,
)


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


@pytest.mark.django_db
def test_foldings_band():
    folding = Foldings(
        processing=Processings(observation=Observations(instrument_config=Instrumentconfigs(frequency=1421.0)))
    )
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
    "ephemeris": {
        "A1": {"val": "1.65284000000000000000"},
        "DM": {"val": "71.800000"},
        "F0": {"val": "273.9479176155999767"},
        "F1": {"val": "-1.2600000000000000e-14"},
        "OM": {"val": "0"},
        "PB": {"val": "1.35405939000000000000"},
        "T0": {"val": "58858.52917739550000000000"},
        "CLK": {"val": "UTC(NIST)"},
        "ECC": {"val": "0"},
        "RAJ": {"val": "17:40:44.5890000"},
        "DECJ": {"val": "-53:40:40.900000"},
        "PSRJ": {"val": "J1740-5340A"},
        "EPHEM": {"val": "DE421"},
        "UNITS": {"val": "TDB"},
        "BINARY": {"val": "BT"},
        "PEPOCH": {"val": "51917.00000000000000000000"},
        "TZRFRQ": {"val": "1273.83100000000000000000"},
        "TZRMJD": {"val": "59074.79479912067542000000"},
        "SOLARN0": {"val": "10.00000000000000000000"},
        "TIMEEPH": {"val": "FB90"},
        "TZRSITE": {"val": "MK"},
        "T2CMETHOD": {"val": "TEMPO"},
        "CORRECT_TROPOSPHERE": {"val": "N"},
    },
    "pipeline_version": "A",
    "tsubint": 8.0,
}


def generate_db_entry(psr, utc, config=default_entry_config):
    """
    Helper method to populate the database with a test entry for a pulsar with name specified by psr and at the time of
    utc. Optionally, all parameters can be modified by providing a entry config dictionary.

    Return the utc as datetime with timezone set
    """
    psr, _ = Pulsars.objects.get_or_create(jname=psr)
    target, _ = Targets.objects.get_or_create(name=psr, raj=config["raj"], decj=config["decj"])
    psrtarget, _ = Pulsartargets.objects.get_or_create(pulsar=psr, target=target)
    telescope, _ = Telescopes.objects.get_or_create(name=config["telescope"])
    program, _ = Programs.objects.get_or_create(name="MeerTime", telescope=telescope)
    proposal, _ = Projects.objects.get_or_create(
        code=config["proposal"], short=config["proposal_short"], program=program
    )

    instrument = Instrumentconfigs.objects.create(
        name=config["name"],
        bandwidth=config["bandwidth"],
        frequency=config["frequency"],
        nchan=config["nchan"],
        npol=config["npol"],
        beam=config["beam"],
    )

    utc_dt = datetime.strptime(f"{utc} +0000", "%Y-%m-%d-%H:%M:%S %z")

    try:
        eph, _ = Ephemerides.objects.get_or_create(
            pulsar=psr,
            created_at=utc_dt,
            created_by=config["name"],
            ephemeris=config["ephemeris"],
            p0=config["p0"],
            dm=config["dm"],
            rm=config["rm"],
            valid_from=utc_dt,
            valid_to=utc_dt + timedelta(days=2),
        )
    except IntegrityError:
        eph = Ephemerides.objects.create(
            pulsar=psr,
            created_at=utc_dt,
            created_by=config["name"],
            ephemeris={
                "A1": {"val": "1.2"},
                "DM": {"val": "2"},
                "F0": {"val": "273.9479176155999767"},
                "F1": {"val": "-1.2600000000000000e-14"},
                "OM": {"val": "0"},
                "PB": {"val": "1.35405939000000000000"},
                "T0": {"val": "58858.52917739550000000000"},
                "CLK": {"val": "UTC(NIST)"},
                "ECC": {"val": "0"},
                "RAJ": {"val": "17:40:44.5890000"},
                "DECJ": {"val": "-53:40:40.900000"},
                "PSRJ": {"val": "J1740-5340A"},
                "EPHEM": {"val": "DE421"},
                "UNITS": {"val": "TDB"},
                "BINARY": {"val": "BT"},
                "PEPOCH": {"val": "51917.00000000000000000000"},
                "TZRFRQ": {"val": "1273.83100000000000000000"},
                "TZRMJD": {"val": "59074.79479912067542000000"},
                "SOLARN0": {"val": "10.00000000000000000000"},
                "TIMEEPH": {"val": "FB90"},
                "TZRSITE": {"val": "MK"},
                "T2CMETHOD": {"val": "TEMPO"},
                "CORRECT_TROPOSPHERE": {"val": "N"},
            },
            p0=1,
            dm=2,
            rm=3,
            valid_from=utc_dt,
            valid_to=utc_dt + timedelta(days=2),
        )

    try:
        pipeline, _ = Pipelines.objects.get_or_create(
            name=config["name"], created_at=utc_dt, revision=config["pipeline_version"], created_by=config["name"]
        )
    except IntegrityError:
        pipeline = Pipelines.objects.create(name="boo", created_at=utc_dt, revision="D", created_by="boo")

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


@pytest.mark.django_db
def test_ephemeris_hash():

    ephemeris = default_entry_config['ephemeris']
    expected = hashlib.md5(json.dumps(ephemeris, sort_keys=True, indent=2).encode("utf-8")).hexdigest()

    utc = "2000-01-01-12:59:12"

    utc_dt = generate_db_entry("J0437-4715", utc)
    psr = Pulsars.objects.get(jname="J0437-4715")

    ephemerides = Ephemerides.objects.get(pulsar=psr)

    assert ephemerides.ephemeris_hash == expected


@pytest.mark.django_db
def test_get_last_session():
    telescope = Telescopes.objects.create(name="TestScope")
    my_timezone = pytz.UTC
    Sessions.objects.create(
        telescope=telescope,
        start=timezone.make_aware(datetime(2021, 1, 15, 8, 45, 23), timezone=my_timezone),
        end=timezone.make_aware(datetime(2021, 1, 15, 15, 0, 0), timezone=my_timezone),
    )
    expected_last_session = Sessions.objects.create(
        telescope=telescope,
        start=timezone.make_aware(datetime(2021, 2, 23, 7, 45), timezone=my_timezone),
        end=timezone.make_aware(datetime(2021, 2, 23, 16, 30), timezone=my_timezone),
    )
    assert Sessions.get_last_session() == expected_last_session


@pytest.mark.django_db
def test_get_session():
    telescope = Telescopes.objects.create(name="TestScope")
    my_timezone = pytz.UTC
    Sessions.objects.create(
        telescope=telescope,
        start=timezone.make_aware(datetime(2021, 1, 15, 8, 45, 23), timezone=my_timezone),
        end=timezone.make_aware(datetime(2021, 1, 15, 15, 0, 0), timezone=my_timezone),
    )
    expected_session = Sessions.objects.create(
        telescope=telescope,
        start=timezone.make_aware(datetime(2021, 2, 23, 7, 45), timezone=my_timezone),
        end=timezone.make_aware(datetime(2021, 2, 23, 16, 30), timezone=my_timezone),
    )
    utc = timezone.make_aware(datetime(2021, 2, 23, 8, 30), timezone=pytz.UTC)
    assert Sessions.get_session(utc) == expected_session
