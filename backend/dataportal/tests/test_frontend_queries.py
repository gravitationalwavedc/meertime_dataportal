# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meertime.settings.settings')
import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient
from dataportal.tests.testing_utils import create_pulsar_with_observations, create_toas_and_residuals
from dataportal.models import Telescope


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy")
    pulsar, telescope, project, ephemeris, template, pipeline_run = create_pulsar_with_observations()
    return client, user, pulsar, telescope, project, ephemeris, template, pipeline_run


def create_test_session():
    t = Telescope.objects.create(name="MeerKat")
    return Sessions.objects.create(
        telescope=t,
        start=FoldPulsarDetail.objects.first().utc,
        end=FoldPulsarDetail.objects.last().utc,
    )@pytest.mark.django_db






@pytest.mark.django_db
@pytest.mark.enable_signals
def test_pulsar_fold_summary_query_no_token():
    client = setup_query_test()[0]
    response = client.execute(
        """
        query {
            pulsarFoldSummary {
                edges {
                    node {
                        id
                    }
                }
            }
        }
    """
    )
    expected_error_message = "You do not have permission to perform this action"
    assert not response.data["pulsarFoldSummary"]
    assert response.errors[0].message == expected_error_message

@pytest.mark.django_db
@pytest.mark.enable_signals
def test_pulsar_fold_summary_query_with_token():
    client, user = setup_query_test()[:2]
    client.authenticate(user)
    response = client.execute(
        """
        query {
            pulsarFoldSummary {
                totalObservations
                totalPulsars
                totalObservationTime
                totalProjectTime
                edges {
                    node {
                        pulsar {name}
                        latestObservation
                        firstObservation
                        mostCommonProject
                        timespan
                        numberOfObservations
                        totalIntegrationHours
                        avgSnPipe
                        highestSn
                        lastSn
                        lastIntegrationMinutes
                    }
                }
            }
        }
    """
    )
    expected = {
        'pulsarFoldSummary': {
            'totalObservations': 2,
            'totalPulsars': 1,
            'totalObservationTime': 0,
            'totalProjectTime': 0,
            'edges': [
                {
                    'node': {
                        'pulsar': {'name': 'J0125-2327'},
                        'latestObservation': '2019-05-14T10:14:18+00:00',
                        'firstObservation': '2019-04-23T06:11:30+00:00',
                        'mostCommonProject': 'RelBin',
                        'timespan': 22,
                        'numberOfObservations': 2,
                        'totalIntegrationHours': 0.36222222222222217,
                        'avgSnPipe': 66.727332977142,
                        'lastSn': 50.0,
                        'highestSn': 100.0,
                        'lastIntegrationMinutes': 17.33333333333333
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)
    response = client.execute(
    """
        query {
            observationSummary (
                pulsar_Name: "All",
                obsType: "fold",
                calibration_Id: "All",
                project_Short: "All",
                telescope_Name: "All",
            ) {
            edges {
                node {
                    observations
                    pulsars
                    observationHours
                    }
                }
            }
            pulsarFoldSummary (
                mainProject: "MeerTIME",
                project: "All",
                band: "All",
            ) {
            edges {
                node {
                    pulsar {name}
                    latestObservation
                    firstObservation
                    allProjects
                    mostCommonProject
                    timespan
                    numberOfObservations
                    lastSn
                    highestSn
                    lowestSn
                    lastIntegrationMinutes
                    maxSnPipe
                    avgSnPipe
                    totalIntegrationHours
                    }
                }
            }
        }
    """
    )
    expected = {
        'observationSummary': {
            'edges': [
                {
                    'node': {
                        'observationHours': 0,
                        'observations': 2,
                        'pulsars': 1
                    }
                }
            ]
        },
        "pulsarFoldSummary": {
            'edges': [
                {
                    'node':{
                        'pulsar': {
                            'name': 'J0125-2327'
                        },
                        'latestObservation': '2019-05-14T10:14:18+00:00',
                        'firstObservation': '2019-04-23T06:11:30+00:00',
                        'allProjects': 'RelBin',
                        'mostCommonProject': 'RelBin',
                        'timespan': 22,
                        'numberOfObservations': 2,
                        'lastSn': 50.0,
                        'highestSn': 100.0,
                        'lowestSn': 50.0,
                        'lastIntegrationMinutes': 17.33333333333333,
                        'maxSnPipe': 106.60035817780525,
                        'avgSnPipe': 66.727332977142,
                        'totalIntegrationHours': 0.36222222222222217
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_detail_query():
    client, user, pulsar, telescope, project, ephemeris, template, pipeline_run = setup_query_test()
    client.authenticate(user)
    create_toas_and_residuals(pulsar, project, ephemeris, pipeline_run, template)
    response = client.execute(
        """
        query {
            observationSummary (
                pulsar_Name: "J0125-2327",
                obsType: "fold",
                calibration_Id: "All",
                project_Short: "All",
                telescope_Name: "All",
            ) {
                edges {
                    node {
                        observations
                        observationHours
                        projects
                        pulsars
                        estimatedDiskSpaceGb
                        timespanDays
                        maxDuration
                        minDuration
                    }
                }
            }
            pulsarFoldResult(
                pulsar: "J0125-2327",
                mainProject: "MeerTime",
            ) {
                description
                ephemerisLink
                toasLink
                edges {
                    node {
                        observation {
                            utcStart
                            duration
                            beam
                            bandwidth
                            nchan
                            band
                            foldNbin
                            nant
                            nantEff
                            project{
                                short
                            }
                            ephemeris {
                                dm
                            }
                        }
                        pipelineRun{
                            dm
                            dmErr
                            rm
                            rmErr
                            sn
                            flux
                            toas (
                                dmCorrected: false,
                                minimumNsubs: true,
                                obsNchan: 1,
                            ) {
                                edges {
                                    node {
                                        freqMhz
                                        mjd
                                        mjdErr
                                        length
                                        residual {
                                            mjd
                                            residualSec
                                            residualSecErr
                                            residualPhase
                                            residualPhaseErr
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
    )
    expected = {
        "observationSummary": {
            "edges": [
                {
                    "node": {
                        "observations": 2,
                        "observationHours": 0,
                        "projects": 1,
                        "pulsars": 1,
                        "estimatedDiskSpaceGb": 0.5770263671875,
                        "timespanDays": 22,
                        "maxDuration": 1039.9999999999998,
                        "minDuration": 263.99999999999994
                    }
                }
            ]
        },
        "pulsarFoldResult": {
            "description": None,
            "ephemerisLink": None,
            "toasLink": None,
            "edges": [
                {
                    "node": {
                        "observation": {
                            "utcStart": "2019-04-23T06:11:30+00:00",
                            "duration": 263.99999999999994,
                            "beam": 1,
                            "bandwidth": 775.75,
                            "nchan": 928,
                            "band": "LBAND",
                            "foldNbin": 1024,
                            "nant": 56,
                            "nantEff": 56,
                            "project": {
                                "short": "RelBin"
                            },
                            "ephemeris": {
                                "dm": 9.593172234774427
                            }
                        },
                        "pipelineRun": {
                            "dm": 20.0,
                            "dmErr": None,
                            "rm": 10.0,
                            "rmErr": None,
                            "sn": 100.0,
                            "flux": 25.0,
                            "toas": {
                                "edges": [
                                    {
                                        "node": {
                                            "freqMhz": 6.0,
                                            "mjd": "7.000000000000",
                                            "mjdErr": 8.0,
                                            "length": 9,
                                            "residual": {
                                                "mjd": "1.000000000000",
                                                "residualSec": 2.0,
                                                "residualSecErr": 3.0,
                                                "residualPhase": 4.0,
                                                "residualPhaseErr": 5.0
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "node": {
                        "observation": {
                            "utcStart": "2019-05-14T10:14:18+00:00",
                            "duration": 1039.9999999999998,
                            "beam": 1,
                            "bandwidth": 775.75,
                            "nchan": 928,
                            "band": "LBAND",
                            "foldNbin": 1024,
                            "nant": 54,
                            "nantEff": 54,
                            "project": {
                                "short": "RelBin"
                            },
                            "ephemeris": {
                                "dm": 9.593172234774427
                            }
                        },
                        "pipelineRun": {
                            "dm": 20.1,
                            "dmErr": None,
                            "rm": 10.1,
                            "rmErr": None,
                            "sn": 50.0,
                            "flux": 25.1,
                            "toas": {
                                "edges": []
                            }
                        }
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


# @pytest.mark.django_db
# @pytest.mark.enable_signals
# def test_searchmode_query():
#     client, user = setup_query_test()[:2]
#     client.authenticate(user)
#     response = client.execute(
#         """
#         query {
#             searchmodeObservations {
#                 totalObservations
#                 totalPulsars
#                 edges {
#                     node {
#                         jname
#                         project
#                         latestObservation
#                         firstObservation
#                         timespan
#                         numberOfObservations
#                     }
#                 }
#             }
#         }
#         """
#     )

#     expected = {
#         "searchmodeObservations": {
#             "totalObservations": 1,
#             "totalPulsars": 1,
#             "edges": [
#                 {
#                     "node": {
#                         "jname": "J0125-2327",
#                         "project": "RelBin",
#                         "latestObservation": "2000-01-21T12:59:12+00:00",
#                         "firstObservation": "2000-01-21T12:59:12+00:00",
#                         "timespan": 1,
#                         "numberOfObservations": 1,
#                     }
#                 }
#             ],
#         }
#     }
#     assert not response.errors
#     assert response.data == expected


# @pytest.mark.django_db
# @pytest.mark.enable_signals
# def test_searchmode_details_query():
#     client, user = setup_query_test()[:2]
#     client.authenticate(user)
#     response = client.execute(
#         """
#         query {
#             searchmodeObservationDetails(jname: "J0125-2327") {
#                 totalObservations
#                 totalProjects
#                 totalTimespanDays
#                 edges {
#                     node {
#                         beam
#                         dec
#                         dm
#                         frequency
#                         length
#                         nantEff
#                         nbit
#                         nchan
#                         project
#                         ra
#                         tsamp
#                         utc
#                     }
#                 }
#             }
#         }
#         """
#     )
#     expected = {
#         "searchmodeObservationDetails": {
#             "totalObservations": 1,
#             "totalProjects": 1,
#             "totalTimespanDays": 0,
#             "edges": [
#                 {
#                     "node": {
#                         "beam": 54,
#                         "dec": "-23:27",
#                         "dm": 2.1,
#                         "frequency": 839,
#                         "length": 0.0,
#                         "nantEff": None,
#                         "nbit": 1,
#                         "nchan": 3,
#                         "project": "RelBin",
#                         "ra": "1:25:",
#                         "tsamp": 1.20,
#                         "utc": "2000-01-21T12:59:12+00:00",
#                     }
#                 }
#             ],
#         }
#     }
#     assert not response.errors
#     assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)
    response = client.execute(
        """
        query {
            observationSummary (
                pulsar_Name: "All",
                obsType: "All",
                calibrationInt: 10,
                project_Short: "All",
                telescope_Name: "All",
            ) {
                edges {
                    node {
                        observations
                        projects
                        pulsars
                    }
                }
            }
            calibration (id: 10) {
                edges {
                    node {
                        id
                        idInt
                        start
                        end
                        observations {
                            edges {
                                node {
                                    id
                                    pulsar {
                                        name
                                    }
                                    utcStart
                                    obsType
                                    duration
                                    frequency
                                    project {
                                        short
                                    }
                                    pulsarFoldResults {
                                        edges {
                                            node {
                                            images {
                                                edges {
                                                    node {
                                                        url
                                                        imageType
                                                        cleaned
                                                    }
                                                }
                                            }
                                                pipelineRun {
                                                    sn
                                                    percentRfiZapped
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
    )
    expected = {
        "observationSummary": {
            "edges": [
                {
                    "node": {
                        "observations": 1,
                        "projects": 1,
                        "pulsars": 1
                    }
                }
            ]
        },
        "calibration": {
            "edges": [
                {
                    "node": {
                        "id": "Q2FsaWJyYXRpb25Ob2RlOjEw",
                        "idInt": 10,
                        "start": "2019-05-14T10:14:18+00:00",
                        "end": "2019-05-14T10:14:18+00:00",
                        "observations": {
                            "edges": [
                                {
                                    "node": {
                                        "id": "T2JzZXJ2YXRpb25Ob2RlOjEw",
                                        "pulsar": {
                                            "name": "J0125-2327"
                                        },
                                        "utcStart": "2019-05-14T10:14:18+00:00",
                                        "obsType": "FOLD",
                                        "duration": 1039.9999999999998,
                                        "frequency": 1283.58203125,
                                        "project": {
                                            "short": "RelBin"
                                        },
                                        "pulsarFoldResults": {
                                            "edges": [
                                                {
                                                    "node": {
                                                        "images": {
                                                            "edges": []
                                                        },
                                                        "pipelineRun": {
                                                            "sn": 50.0,
                                                            "percentRfiZapped": None
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_list_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute(
        """
        query {
        calibration {
            edges {
                node {
                    id
                    idInt
                    start
                    end
                    allProjects
                    nObservations
                    nAntMin
                    nAntMax
                    totalIntegrationTimeSeconds
                    }
                }
            }
        }
        """
    )
    expected = {
        "calibration": {
            "edges": [
                {
                    "node": {
                        "id": "Q2FsaWJyYXRpb25Ob2RlOjEy",
                        "idInt": 12,
                        "start": "2019-05-14T10:14:18+00:00",
                        "end": "2019-05-14T10:14:18+00:00",
                        "allProjects": "RelBin",
                        "nObservations": 1,
                        "nAntMin": 54,
                        "nAntMax": 54,
                        "totalIntegrationTimeSeconds": 1039.9999999999998
                    }
                },
                {
                    "node": {
                        "id": "Q2FsaWJyYXRpb25Ob2RlOjEx",
                        "idInt": 11,
                        "start": "2019-04-23T06:11:30+00:00",
                        "end": "2019-04-23T06:11:30+00:00",
                        "allProjects": "RelBin",
                        "nObservations": 1,
                        "nAntMin": 56,
                        "nAntMax": 56,
                        "totalIntegrationTimeSeconds": 263.99999999999994
                    }
                }
            ]
        }
    }
    assert not response.errors
    import json
    print(json.dumps(response.data, indent=4))
    assert response.data == expected
