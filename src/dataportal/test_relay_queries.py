import pytest
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from graphql.error.located_error import GraphQLLocatedError
from graphql_jwt.testcases import JSONWebTokenClient
from meertime.schema import schema
from graphql_relay import from_global_id, to_global_id
from .models import Pulsars, Observations, Utcs, Proposals, Searchmode


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy")
    proposal = Proposals.objects.create(proposal="SCI_thing_MB", proposal_short="cool proposal")
    pulsar = Pulsars.objects.create(jname="J111-2222")
    utc = Utcs.objects.create(utc_ts=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"))
    Observations.objects.create(
        pulsar=pulsar,
        utc=utc,
        proposal=proposal,
        beam=1,
        frequency=300,
        snr_pipe=4,
        length=20,
        bw=775.75,
        snr_spip=741.3,
        rm_pipe=1,
        dm_pipe=2,
        dm_fold=4,
        nchan=4,
        nbin=2,
        nsubint=5,
        mjd="Some text",
        mjd_int=4,
        mjd_frac=12,
        pa=12.23,
        observer="Buffy",
        nant=42,
    )
    Searchmode.objects.create(
        pulsar=pulsar,
        utc=utc,
        proposal=proposal,
        beam=2,
        comment="A comment",
        length=4,
        tsamp=2.2,
        bw=381.12,
        frequency=375.12954,
        nchan=6,
        nbit=5,
        npol=4,
        nant=12,
        nant_eff=22,
        dm=41.21,
        ra="-515.123",
        dec="12:12:21",
    )
    return client, user


@pytest.mark.django_db
def test_fold_query_no_token():
    client, _ = setup_query_test()
    response = client.execute(
        """
        query {
            relayObservations(mode:"observations") {
                edges {
                    node {
                        jname
                    }
                }
            }
        }
    """
    )
    expected_error_message = "You do not have permission to perform this action"
    assert not response.data["relayObservations"]
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
def test_fold_query_with_token():
    client, user = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            relayObservations(mode:"observations", proposal:"All", band:"All") {
                totalObservations
                totalPulsars
                totalObservationTime
                edges {
                    node {
                        jname
                        last
                        first
                        proposalShort
                        timespan
                        nobs
                        totalTintH
                        avgSnr5min
                        maxSnr5min
                        latestSnr
                        latestTintM
                    }
                }
            }
        }
    """
    )
    expected = {
        "relayObservations": {
            "totalObservations": 1,
            "totalPulsars": 1,
            "totalObservationTime": 0,
            "edges": [
                {
                    "node": {
                        "jname": "J111-2222",
                        "last": "2000-01-01T12:59:12+00:00",
                        "first": "2000-01-01T12:59:12+00:00",
                        "proposalShort": "cool proposal",
                        "timespan": "0",
                        "nobs": 1,
                        "totalTintH": 0.0,
                        "avgSnr5min": 15.5,
                        "maxSnr5min": 15.5,
                        "latestSnr": 741.3,
                        "latestTintM": 0.3,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_fold_query_with_proposal_and_band():
    client, user = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            relayObservations(mode:"observations", proposal:"cool proposal", band:"UFH"){
                totalObservations
                totalObservationTime
                totalPulsars
                edges {
                    node {
                        jname
                    }
                }
            }
        }
    """
    )
    expected = {
        "relayObservations": {
            "totalObservations": 1,
            "totalObservationTime": 0,
            "totalPulsars": 1,
            "edges": [{"node": {"jname": "J111-2222"}}],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_fold_detail_query():
    client, user = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            relayObservationDetails(jname:"J111-2222") {
            jname
            totalObservations
            totalObservationHours
            totalProjects
            totalEstimatedDiskSpace
            totalTimespanDays
            ephemeris
            ephemerisUpdatedAt
            edges {
              node {
                utc
                proposalShort
                length
                beam
                bw
                nchan
                band
                nbin
                nant
                nantEff
                dmFold
                dmPipe
                rmPipe
                snrPipe
                snrSpip
              }
            }
          }
        }
        """
    )
    expected = {
        "relayObservationDetails": {
            "jname": "J111-2222",
            "totalObservations": 1,
            "totalObservationHours": 0.0,
            "totalProjects": 1,
            "totalEstimatedDiskSpace": "192\xa0bytes",
            "totalTimespanDays": 0,
            "ephemeris": None,
            "ephemerisUpdatedAt": None,
            "edges": [
                {
                    "node": {
                        "utc": "2000-01-01-12:59:12",
                        "proposalShort": "cool proposal",
                        "length": 0.3,
                        "beam": 1,
                        "bw": 775.75,
                        "nchan": 4,
                        "band": "Unknown",
                        "nbin": 2,
                        "nant": 42,
                        "nantEff": None,
                        "dmFold": 4.0,
                        "dmPipe": 2.0,
                        "rmPipe": 1.0,
                        "snrPipe": 4.0,
                        "snrSpip": 741.3,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_serachmode_detail_query():
    client, user = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            relaySearchmodeDetails(jname:"J111-2222"){
                jname
                totalObservations
                totalProjects
                totalObservationHours
                totalTimespanDays
                edges {
                  node {
                    utc
                    proposalShort
                    beam
                    comment
                    length
                    tsamp
                    bw
                    frequency
                    nchan
                    nbit
                    npol
                    nant
                    nantEff
                    dm
                    ra
                    dec
                 }
              }
           }
        } 
        """
    )
    expected = {
        'relaySearchmodeDetails': {
            'jname': 'J111-2222',
            'totalObservations': 1,
            'totalProjects': 1,
            'totalObservationHours': 0.0,
            'totalTimespanDays': 0,
            'edges': [
                {
                    'node': {
                        'utc': '2000-01-01-12:59:12',
                        'proposalShort': 'cool proposal',
                        'beam': 2,
                        'comment': 'A comment',
                        'length': 0.1,
                        'tsamp': 2.2,
                        'bw': 381.12,
                        'frequency': 375.12954,
                        'nchan': 6,
                        'nbit': 5,
                        'npol': 4,
                        'nant': 12,
                        'nantEff': 22,
                        'dm': 41.21,
                        'ra': '-515.123',
                        'dec': '12:12:21',
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_observation_model_query():
    client, user = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            relayObservationModel(jname:"J111-2222", utc:"2000-01-01-12:59:12", beam:1){
            jname
            beam
            schedule
            phaseup
            utc
            proposal
            frequency
            bw
            ra
            dec
            length
            snrSpip
            nbin
            nchan
            nsubint
            nant
            profile
          }
        }
        """
    )
    expected = {
        'relayObservationModel': {
            'jname': 'J111-2222',
            'beam': 1,
            'utc': '2000-01-01 12:59:12+00:00',
            'proposal': 'SCI_thing_MB',
            'frequency': 300.0,
            'bw': 775.75,
            'ra': None,
            'dec': None,
            'length': 20.0,
            'snrSpip': 741.3,
            'nbin': 2,
            'nchan': 4,
            'nsubint': 5,
            'phaseup': None,
            'schedule': None,
            'nant': 42,
            'profile': '',
        }
    }
    assert response.data == expected
