# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meertime.settings.settings')
import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient
from dataportal.tests.testing_utils import create_pulsar_with_observations, create_toas_and_residuals


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy")
    pulsar, telescope, project, ephemeris, template, pipeline_run = create_pulsar_with_observations()
    return client, user, pulsar, telescope, project, ephemeris, template, pipeline_run



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
                mainProject: "MeerTIME",
                project_Short: "All",
                band: "All",
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
                mainProject: "MeerTIME",
                project_Short: "All",
                band: "All",
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
                toasLink
                residualEphemeris {
                    ephemerisData
                    createdAt
                }
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
                        "estimatedDiskSpaceGb": 0.5770263671874999,
                        "timespanDays": 22,
                        "maxDuration": 1039.9999999999998,
                        "minDuration": 263.99999999999994
                    }
                }
            ]
        },
        "pulsarFoldResult": {
            "description": None,
            "toasLink": None,
            "residualEphemeris": {
                'ephemerisData': '"{\\"PSRJ\\": \\"J0125-2327\\", \\"RAJ\\": \\"01:25:01.0743144\\", \\"RAJ_ERR\\": 1.2799484500709e-06, \\"DECJ\\": \\"-23:27:08.13506\\", \\"DECJ_ERR\\": 1.918386314202124e-05, \\"F0\\": 272.08108426663085, \\"F0_ERR\\": 6.475925761376348e-13, \\"F1\\": -1.3634461197849394e-15, \\"F1_ERR\\": 2.8611605694875965e-20, \\"PEPOCH\\": 59040.0, \\"POSEPOCH\\": 59040.0, \\"POSEPOCH_ERR\\": 0.0, \\"DMEPOCH\\": 59000.0, \\"DM\\": 9.593172234774427, \\"DM_ERR\\": 0.000840292114365348, \\"DM1\\": -4.550186362449281e-05, \\"DM1_ERR\\": 2.866849975313738e-05, \\"DM2\\": 0.0008473829314709747, \\"DM2_ERR\\": 4.445334526905498e-05, \\"DM3\\": -0.0012503975851400912, \\"DM3_ERR\\": 5.554336608194772e-05, \\"PMRA\\": 37.12252111446872, \\"PMRA_ERR\\": 0.016981816168441643, \\"PMDEC\\": 10.783483810973774, \\"PMDEC_ERR\\": 0.020762535094482653, \\"PX\\": 0.9625766364575671, \\"PX_ERR\\": 0.04876126384389193, \\"BINARY\\": \\"ELL1\\", \\"PB\\": 7.277199751931904, \\"PB_ERR\\": 1.2218737166e-10, \\"A1\\": 4.729805939931686, \\"A1_ERR\\": 1.8566063704366e-07, \\"XDOT\\": -3.724535301864433e-14, \\"XDOT_ERR\\": 9.611886578212533e-16, \\"TASC\\": 57089.073682561524, \\"TASC_ERR\\": 3.74730327085e-08, \\"EPS1\\": 6.04039114241693e-08, \\"EPS1_ERR\\": 1.036524801089e-08, \\"EPS2\\": 3.823849574883707e-07, \\"EPS2_ERR\\": 9.71727142073e-09, \\"START\\": \\"2019-04-23T06:13:48.323095Z\\", \\"FINISH\\": \\"2022-07-27T00:46:33.004474Z\\", \\"TRACK\\": -2.0, \\"TZRMJD\\": 59191.764430068564, \\"TZRFRQ\\": 1453.265767, \\"TZRSITE\\": \\"meerkat\\", \\"FD1\\": -3.7031665758945584e-05, \\"FD1_ERR\\": 6.70814076275845e-06, \\"FD2\\": 2.9633689096210766e-05, \\"FD2_ERR\\": 4.68543125704137e-06, \\"TRES\\": 0.477, \\"EPHVER\\": 5.0, \\"NE_SW\\": 4.0, \\"CLK\\": \\"TT(BIPM2019)\\", \\"MODE\\": 1.0, \\"UNITS\\": \\"TCB\\", \\"TIMEEPH\\": \\"IF99\\", \\"DILATEFREQ\\": \\"Y\\", \\"PLANET_SHAPIRO\\": \\"N\\", \\"T2CMETHOD\\": \\"IAU2000B\\", \\"CORRECT_TROPOSPHERE\\": \\"Y\\", \\"EPHEM\\": \\"DE438\\", \\"NITS\\": 1.0, \\"NTOA\\": 1233.0, \\"CHI2R\\": 1.2315, \\"CHI2R_ERR\\": 1213.0, \\"TIMEOFFSETS\\": [{\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58526_59621_1K\\", \\"display\\": \\"-1.1962616822e-06\\", \\"offset\\": \\"-1.1962616822e-06\\", \\"fit\\": \\"-1.1962616822e-06\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58550_58690_1K\\", \\"display\\": \\"-0.000306243\\", \\"offset\\": \\"-0.000306243\\", \\"fit\\": \\"-0.000306243\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58526.21089_1K\\", \\"display\\": \\"-2.4628e-05\\", \\"offset\\": \\"-2.4628e-05\\", \\"fit\\": \\"-2.4628e-05\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58550.14921_1K\\", \\"display\\": \\"2.463e-05\\", \\"offset\\": \\"2.463e-05\\", \\"fit\\": \\"2.463e-05\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58550.14921B_1K\\", \\"display\\": \\"-1.196e-06\\", \\"offset\\": \\"-1.196e-06\\", \\"fit\\": \\"-1.196e-06\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58557.14847_1K\\", \\"display\\": \\"-4.785e-06\\", \\"offset\\": \\"-4.785e-06\\", \\"fit\\": \\"-4.785e-06\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58575.9591_1K\\", \\"display\\": \\"5.981308411e-07\\", \\"offset\\": \\"5.981308411e-07\\", \\"fit\\": \\"5.981308411e-07\\"}], \\"DM_SERIES\\": \\"TAYLOR\\", \\"P0\\": 0.003675374944551572, \\"P0_ERR\\": 9e-18}"',
            },
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
    del response.data["pulsarFoldResult"]["residualEphemeris"]["createdAt"]
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
                mainProject: "All",
                project_Short: "All",
                band: "All",
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
