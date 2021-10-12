import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient
from web_cache.test_signals import create_pulsar_with_observations
from web_cache.models import FoldPulsarDetail
from dataportal.models import Telescopes, Sessions


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy")
    jname = create_pulsar_with_observations()
    return client, user, jname


@pytest.mark.django_db
def test_fold_query_no_token():
    client, _, _ = setup_query_test()
    response = client.execute(
        """
        query {
            foldObservations {
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
    assert not response.data["foldObservations"]
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
def test_fold_query_with_token():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            foldObservations {
                totalObservations
                totalPulsars
                totalObservationTime
                edges {
                    node {
                        jname
                        latestObservation
                        firstObservation
                        project
                        timespan
                        numberOfObservations
                        totalIntegrationHours
                        avgSnPipe
                        maxSnPipe
                        lastSnRaw
                        lastIntegrationMinutes
                    }
                }
            }
        }
    """
    )
    expected = {
        'foldObservations': {
            'totalObservations': 1,
            'totalPulsars': 1,
            'totalObservationTime': 0,
            'edges': [
                {
                    'node': {
                        'jname': 'J0125-2327',
                        'latestObservation': '2000-01-21T12:59:12+00:00',
                        'firstObservation': '2000-01-21T12:59:12+00:00',
                        'project': 'Relbin',
                        'timespan': 1,
                        'numberOfObservations': 1,
                        'totalIntegrationHours': 0.0,
                        'avgSnPipe': None,
                        'maxSnPipe': None,
                        'lastSnRaw': 67.8,
                        'lastIntegrationMinutes': 0.1,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_fold_query_with_proposal_and_band():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            foldObservations {
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
        'foldObservations': {
            'totalObservations': 1,
            'totalObservationTime': 0,
            'totalPulsars': 1,
            'edges': [{'node': {'jname': 'J0125-2327'}}],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_fold_detail_query():
    client, user, jname = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        f"""
        query {{
            foldObservationDetails(jname:"{jname}") {{
            totalObservations
            totalObservationHours
            totalProjects
            totalEstimatedDiskSpace
            totalTimespanDays
            edges {{
              node {{
                utc
                project
                length
                beam
                bw
                nchan
                band
                nbin
                nant
                nantEff
                dmFold
                dmMeerpipe
                rmMeerpipe
                snBackend
                snMeerpipe
              }}
            }}
          }}
        }}
        """
    )
    expected = {
        'foldObservationDetails': {
            'totalObservations': 1,
            'totalObservationHours': 0,
            'totalProjects': 1,
            'totalEstimatedDiskSpace': '77.6\xa0KB',
            'totalTimespanDays': 1,
            'edges': [
                {
                    'node': {
                        'utc': '2000-01-21T12:59:12+00:00',
                        'project': 'Relbin',
                        'length': 0,
                        'beam': 54,
                        'bw': 11.0,
                        'nchan': 21,
                        'band': 'UHF',
                        'nbin': 43,
                        'nant': None,
                        'nantEff': None,
                        'dmFold': None,
                        'dmMeerpipe': None,
                        'rmMeerpipe': None,
                        'snBackend': 67.8,
                        'snMeerpipe': None,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_searchmode_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            searchmodeObservations {
                totalObservations
                totalPulsars
                edges {
                    node {
                        jname
                        project
                        latestObservation
                        firstObservation
                        timespan
                        numberOfObservations
                    }
                }
            }
        }
        """
    )

    expected = {
        'searchmodeObservations': {
            'totalObservations': 2,
            'totalPulsars': 1,
            'edges': [
                {
                    'node': {
                        'jname': 'J0125-2327',
                        'project': 'Relbin',
                        'latestObservation': '2000-01-21T12:59:12+00:00',
                        'firstObservation': '2000-01-01T12:59:12+00:00',
                        'timespan': 21,
                        'numberOfObservations': 2,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_session_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    t = Telescopes.objects.create(name="MeerKat")
    Sessions.objects.create(
        telescope=t, start=FoldPulsarDetail.objects.first().utc, end=FoldPulsarDetail.objects.last().utc
    )

    response = client.execute(
        """
        query {
            lastSession {
                start
                end
                numberOfObservations
                numberOfPulsars
                edges {
                    node {
                        jname
                        project
                        utc
                        frequency
                        profileHi
                        phaseVsTimeHi
                        phaseVsFrequencyHi
                        profileLo
                        phaseVsTimeLo
                        phaseVsFrequencyLo
                    }
                }
            }
        }
        """
    )

    expected = {
        'lastSession': {
            'start': '2000-01-21T12:59:12+00:00',
            'end': '2000-01-21T12:59:12+00:00',
            'numberOfObservations': 1,
            'numberOfPulsars': 1,
            'edges': [
                {
                    'node': {
                        'jname': 'J0125-2327',
                        'project': 'Relbin',
                        'utc': '2000-01-21T12:59:12+00:00',
                        'frequency': 839.0,
                        'profileHi': None,
                        'phaseVsTimeHi': None,
                        'phaseVsFrequencyHi': None,
                        'profileLo': None,
                        'phaseVsTimeLo': None,
                        'phaseVsFrequencyLo': None,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected
