import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient
from web_cache.testing_utils import create_pulsar_with_observations
from web_cache.models import FoldPulsarDetail, SessionDisplay
from dataportal.models import Telescopes, Sessions


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy")
    jname = create_pulsar_with_observations()
    return client, user, jname


def create_test_session():
    t = Telescopes.objects.create(name="MeerKat")
    return Sessions.objects.create(
        telescope=t,
        start=FoldPulsarDetail.objects.first().utc,
        end=FoldPulsarDetail.objects.last().utc,
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
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
@pytest.mark.enable_signals
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
                totalProjectTime
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
        "foldObservations": {
            "totalObservations": 1,
            "totalPulsars": 1,
            "totalObservationTime": 0,
            "totalProjectTime": 0,
            "edges": [
                {
                    "node": {
                        "jname": "J0125-2327",
                        "latestObservation": "2000-01-21T12:59:12+00:00",
                        "firstObservation": "2000-01-21T12:59:12+00:00",
                        "project": "RelBin",
                        "timespan": 1,
                        "numberOfObservations": 1,
                        "totalIntegrationHours": 0.0,
                        "avgSnPipe": None,
                        "maxSnPipe": None,
                        "lastSnRaw": 67.8,
                        "lastIntegrationMinutes": 0.1,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
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
        "foldObservations": {
            "totalObservations": 1,
            "totalObservationTime": 0,
            "totalPulsars": 1,
            "edges": [{"node": {"jname": "J0125-2327"}}],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
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
            description
            maxPlotLength
            minPlotLength
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
                flux
                ephemeris
                restricted
                images {{
                    edges {{
                        node {{
                            process
                            resolution
                            plotType
                            genericPlotType
                            imageType
                            url
                        }}
                    }}
                }}
              }}
            }}
          }}
        }}
        """
    )
    expected = {
        "foldObservationDetails": {
            "totalObservations": 1,
            "totalObservationHours": 0,
            "totalProjects": 1,
            "totalEstimatedDiskSpace": "74.1\xa0KB",
            "totalTimespanDays": 1,
            "description": None,
            "maxPlotLength": 4,
            "minPlotLength": 4,
            "edges": [
                {
                    "node": {
                        "utc": "2000-01-21T12:59:12+00:00",
                        "project": "RelBin",
                        "length": 0.0,
                        "beam": 54,
                        "bw": 11.00,
                        "nchan": 21,
                        "band": "UHF",
                        "nbin": 43,
                        "nant": None,
                        "nantEff": None,
                        "dmFold": None,
                        "dmMeerpipe": 24.00,
                        "rmMeerpipe": 25.00,
                        "snBackend": 67.8,
                        "snMeerpipe": 42.1,
                        "flux": 1.22,
                        "restricted": False,
                        "images": {
                            "edges": [
                                {
                                    "node": {
                                        "genericPlotType": None,
                                        "imageType": None,
                                        "plotType": None,
                                        "process": None,
                                        "resolution": None,
                                        "url": "",
                                    }
                                }
                            ]
                        },
                        "ephemeris": "{}",
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
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
        "searchmodeObservations": {
            "totalObservations": 1,
            "totalPulsars": 1,
            "edges": [
                {
                    "node": {
                        "jname": "J0125-2327",
                        "project": "RelBin",
                        "latestObservation": "2000-01-21T12:59:12+00:00",
                        "firstObservation": "2000-01-21T12:59:12+00:00",
                        "timespan": 1,
                        "numberOfObservations": 1,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_searchmode_details_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            searchmodeObservationDetails(jname: "J0125-2327") {
                totalObservations
                totalProjects
                totalTimespanDays
                edges {
                    node {
                        beam
                        dec
                        dm
                        frequency
                        length
                        nantEff
                        nbit
                        nchan
                        project
                        ra
                        tsamp
                        utc
                    }
                }
            }
        }
        """
    )
    expected = {
        "searchmodeObservationDetails": {
            "totalObservations": 1,
            "totalProjects": 1,
            "totalTimespanDays": 0,
            "edges": [
                {
                    "node": {
                        "beam": 54,
                        "dec": "-23:27",
                        "dm": 2.1,
                        "frequency": 839,
                        "length": 0.0,
                        "nantEff": None,
                        "nbit": 1,
                        "nchan": 3,
                        "project": "RelBin",
                        "ra": "1:25:",
                        "tsamp": 1.20,
                        "utc": "2000-01-21T12:59:12+00:00",
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_last_session_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    create_test_session()
    response = client.execute(
        """
        query {
            sessionDisplay {
                start
                end
                numberOfObservations
                numberOfPulsars
                sessionPulsars {
                    edges {
                        node {
                            jname
                            project
                            utc
                            frequency
                            fluxHi
                            phaseVsTimeHi
                            phaseVsFrequencyHi
                            fluxLo
                            phaseVsTimeLo
                            phaseVsFrequencyLo
                        }
                    }
                }
            }
        }
        """
    )
    expected = {
        "sessionDisplay": {
            "start": "2000-01-21T12:59:12+00:00",
            "end": "2000-01-21T12:59:12+00:00",
            "numberOfObservations": 2,
            "numberOfPulsars": 2,
            "sessionPulsars": {
                "edges": [
                    {
                        "node": {
                            "jname": "J0125-2327",
                            "project": "RelBin",
                            "utc": "2000-01-21T12:59:12+00:00",
                            "frequency": 839.0,
                            "fluxHi": None,
                            "phaseVsTimeHi": None,
                            "phaseVsFrequencyHi": None,
                            "fluxLo": None,
                            "phaseVsTimeLo": None,
                            "phaseVsFrequencyLo": None,
                        }
                    },
                    {
                        "node": {
                            "jname": None,
                            "project": "RelBin",
                            "utc": "2000-01-21T12:59:12+00:00",
                            "frequency": 839,
                            "fluxHi": None,
                            "phaseVsTimeHi": None,
                            "phaseVsFrequencyHi": None,
                            "fluxLo": None,
                            "phaseVsTimeLo": None,
                            "phaseVsFrequencyLo": None,
                        }
                    },
                ]
            },
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_list_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    session = create_test_session()
    SessionDisplay.update_or_create(session)

    response = client.execute(
        """
        query {
            sessionList {
                edges {
                    node {
                        start
                        end
                        numberOfPulsars
                        numberOfObservations
                        frequency
                        projects
                        totalIntegration
                        nDishMin
                        nDishMax
                        zapFraction
                    }
                }
            }
        }
        """
    )
    expected = {
        "sessionList": {
            "edges": [
                {
                    "node": {
                        "start": "2000-01-21T12:59:12+00:00",
                        "end": "2000-01-21T12:59:12+00:00",
                        "numberOfPulsars": 2,
                        "numberOfObservations": 2,
                        "frequency": 839.0,
                        "projects": "RelBin",
                        "totalIntegration": 8,
                        "nDishMin": None,
                        "nDishMax": None,
                        "zapFraction": 0.0,
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_display_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    session = create_test_session()
    SessionDisplay.update_or_create(session)

    response = client.execute(
        """
        query {
            sessionDisplay {
                start
                end
                sessionPulsars {
                    start
                    end
                    numberOfObservations
                    numberOfPulsars
                    edges {
                        node {
                            integrations
                        }
                    }
                }
            }
        }
        """
    )

    expected = {
        "sessionDisplay": {
            "start": "2000-01-21T12:59:12+00:00",
            "end": "2000-01-21T12:59:12+00:00",
            "sessionPulsars": {
                "start": "2000-01-21T12:59:12+00:00",
                "end": "2000-01-21T12:59:12+00:00",
                "numberOfObservations": 2,
                "numberOfPulsars": 2,
                "edges": [{"node": {"integrations": 4}}, {"node": {"integrations": 4}}],
            },
        }
    }

    assert not response.errors
    assert response.data == expected
