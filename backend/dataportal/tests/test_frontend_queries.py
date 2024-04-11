import os
import json
import pytest

from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient

from dataportal.tests.testing_utils import (
    setup_query_test,
    upload_toa_files,
    create_basic_data,
    create_observation_pipeline_run_toa,
    TEST_DATA_DIR,
)
from utils.tests.test_toa import TOA_FILES


FOLD_SUMMARY_QUERY = """
    query {
        pulsarFoldSummary (
            first: 1
        ) {
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


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_pulsar_fold_summary_query_no_token():
    client = setup_query_test()[0]
    response = client.execute(FOLD_SUMMARY_QUERY)
    expected_error_message = "You do not have permission to perform this action"
    assert not response.data["pulsarFoldSummary"]
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_pulsar_fold_summary_query_with_token():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute(FOLD_SUMMARY_QUERY)
    print(json.dumps(response.data, indent=4))
    assert not response.errors
    assert response.data == {
        "pulsarFoldSummary": {
            "totalObservations": 1,
            "totalPulsars": 1,
            "totalObservationTime": 0,
            "totalProjectTime": 0,
            "edges": [
                {
                    "node": {
                        "pulsar": {
                            "name": "J0437-4715"
                        },
                        "latestObservation": "2023-04-17T15:08:35+00:00",
                        "firstObservation": "2023-04-17T15:08:35+00:00",
                        "mostCommonProject": "PTA",
                        "timespan": 1,
                        "numberOfObservations": 1,
                        "totalIntegrationHours": 0.07097196062305294,
                        "avgSnPipe": 108.35924627749955,
                        "highestSn": 100.0,
                        "lastSn": 100.0,
                        "lastIntegrationMinutes": 4.258317637383176
                    }
                }
            ]
        }
    }


FOLD_QUERY = """
query {{
    observationSummary(
        pulsar_Name: "J0125-2327"
        obsType: "fold"
        calibration_Id: "All"
        mainProject: "MeerTIME"
        project_Short: "All"
        band: "{band}"
    ) {{
        edges {{
            node {{
                observations
                pulsars
                observationHours
            }}
        }}
    }}
    pulsarFoldSummary (
        mainProject: "MeerTIME"
        project: "All"
        band: "{band}"
        first: 1
    ) {{
        edges {{
            node {{
                pulsar {{
                    name
                }}
                latestObservation
                latestObservationBeam
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
            }}
        }}
    }}
}}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute(FOLD_QUERY.format(band="All"))
    print(json.dumps(response.data, indent=4))
    assert not response.errors
    assert response.data == {
        "observationSummary": {
            "edges": [
                {
                    "node": {
                        "observations": 3,
                        "pulsars": 1,
                        "observationHours": 0
                    }
                }
            ]
        },
        "pulsarFoldSummary": {
            "edges": [
                {
                    "node": {
                        "pulsar": {
                            "name": "J0437-4715"
                        },
                        "latestObservation": "2023-04-17T15:08:35+00:00",
                        "latestObservationBeam": 1,
                        "firstObservation": "2023-04-17T15:08:35+00:00",
                        "allProjects": "PTA",
                        "mostCommonProject": "PTA",
                        "timespan": 1,
                        "numberOfObservations": 1,
                        "lastSn": 100.0,
                        "highestSn": 100.0,
                        "lowestSn": 100.0,
                        "lastIntegrationMinutes": 4.258317637383176,
                        "maxSnPipe": 108.35924627749955,
                        "avgSnPipe": 108.35924627749955,
                        "totalIntegrationHours": 0.07097196062305294
                    }
                }
            ]
        }
    }

    response = client.execute(FOLD_QUERY.format(band="UHF"))
    print(json.dumps(response.data, indent=4))
    assert not response.errors
    assert response.data == {
        "observationSummary": {
            "edges": [
                {
                    "node": {
                        "observations": 1,
                        "pulsars": 1,
                        "observationHours": 0
                    }
                }
            ]
        },
        "pulsarFoldSummary": {
            "edges": [
                {
                    "node": {
                        "pulsar": {
                            "name": "J0125-2327"
                        },
                        "latestObservation": "2020-07-10T05:07:28+00:00",
                        "latestObservationBeam": 2,
                        "firstObservation": "2019-04-23T06:11:30+00:00",
                        "allProjects": "PTA",
                        "mostCommonProject": "PTA",
                        "timespan": 444,
                        "numberOfObservations": 3,
                        "lastSn": 100.0,
                        "highestSn": 100.0,
                        "lowestSn": 100.0,
                        "lastIntegrationMinutes": 17.05475670588235,
                        "maxSnPipe": 106.60035817780525,
                        "avgSnPipe": 71.48481915250221,
                        "totalIntegrationHours": 0.6464681673202614
                    }
                }
            ]
        }
    }


FOLD_DETAIL_QUERY = """
    query {
        observationSummary (
            pulsar_Name: "J0125-2327"
            obsType: "fold"
            calibration_Id: "All"
            mainProject: "MeerTIME"
            project_Short: "All"
            band: "All"
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
            mainProject: "MeerTIME"
            first: 1
        ) {
        residualEphemeris {
            ephemerisData
            createdAt
        }
        description
        edges {
            node {
                observation {
                    id
                    utcStart
                    dayOfYear
                    binaryOrbitalPhase
                    duration
                    beam
                    bandwidth
                    nchan
                    band
                    foldNbin
                    nant
                    nantEff
                    restricted
                    embargoEndDate
                    project {
                        short
                    }
                    ephemeris {
                        dm
                    }
                    calibration {
                        idInt
                    }
                }
                pipelineRun {
                    dm
                    dmErr
                    rm
                    rmErr
                    sn
                    flux
                }
            }
        }
    }
}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_detail_query():
    client, user, _, _, _, _, _, _, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(FOLD_DETAIL_QUERY)

    assert not response.errors
    del response.data["pulsarFoldResult"]["residualEphemeris"]["createdAt"]
    assert response.data == {
        "observationSummary": {
            "edges": [
                {
                    "node": {
                        "observations": 3,
                        "observationHours": 0,
                        "projects": 1,
                        "pulsars": 1,
                        "estimatedDiskSpaceGb": 1.0766774425551469,
                        "timespanDays": 444,
                        "maxDuration": 1039.9999999999998,
                        "minDuration": 263.99999999999994
                    }
                }
            ]
        },
        "pulsarFoldResult": {
            "residualEphemeris": {
                "ephemerisData": "\"{\\\"PSRJ\\\": \\\"J0125-2327\\\", "
                "\\\"RAJ\\\": \\\"01:25:01.05950406\\\", "
                "\\\"DECJ\\\": \\\"-23:27:08.1841977\\\", "
                "\\\"DM\\\": 9.59243, "
                "\\\"PEPOCH\\\": 57089.119311, "
                "\\\"F0\\\": 272.08108871500735, "
                "\\\"F1\\\": -1.361e-15, "
                "\\\"PMRA\\\": 40.3478, "
                "\\\"PMDEC\\\": 5.6682, "
                "\\\"DMEPOCH\\\": 58595.551, "
                "\\\"BINARY\\\": \\\"ELL1\\\", "
                "\\\"PB\\\": 7.27719962431521, "
                "\\\"A1\\\": 4.729804686, "
                "\\\"TASC\\\": 57089.07346805, "
                "\\\"EPS1\\\": -1.05e-08, "
                "\\\"EPS2\\\": 2.657e-07, "
                "\\\"CLK\\\": \\\"UNCORR\\\", "
                "\\\"EPHEM\\\": \\\"DE405\\\", "
                "\\\"TZRMJD\\\": 57089.810474242644, "
                "\\\"TZRFRQ\\\": 368.58, "
                "\\\"TZRSITE\\\": 1.0, "
                "\\\"PX\\\": 7.2143, "
                "\\\"EPHVER\\\": 2.0, "
                "\\\"UNITS\\\": \\\"TDB\\\", "
                "\\\"F0_ERR\\\": null, "
                "\\\"P0\\\": 0.0036753748844612086, "
                "\\\"P0_ERR\\\": null, "
                "\\\"START\\\": \\\"1970-01-01T00:00:00\\\", "
                "\\\"FINISH\\\": \\\"2106-02-07T06:28:15\\\"}\""
            },
            "description": "PSR J0125-2327 is a millisecond pulsar with a period of 3.68 milliseconds and has a small "
            "dispersion measure of 9.597 pc/cm^3. It is a moderately bright pulsar with a 1400 MHz catalogue flux "
            "density of 2.490 mJy. PSR J0125-2327 is a Southern Hemisphere pulsar. PSR J0125-2327 has no measured "
            "period derivative. The estimated distance to J0125-2327 is 873 pc. This pulsar appears to be solitary.",
            "edges": [
                {
                    "node": {
                        "observation": {
                            "id": "T2JzZXJ2YXRpb25Ob2RlOjI2",
                            "utcStart": "2019-04-23T06:11:30+00:00",
                            "dayOfYear": 113.25798611111111,
                            "binaryOrbitalPhase": 0.1107189377501644,
                            "duration": 263.99999999999994,
                            "beam": 1,
                            "bandwidth": 775.75,
                            "nchan": 928,
                            "band": "LBAND",
                            "foldNbin": 1024,
                            "nant": 56,
                            "nantEff": 56,
                            "restricted": False,
                            "embargoEndDate": "2020-10-22T06:11:30+00:00",
                            "project": {
                                "short": "PTA"
                            },
                            "ephemeris": {
                                "dm": 9.59243
                            },
                            "calibration": {
                                "idInt": 26
                            }
                        },
                        "pipelineRun": {
                            "dm": 20.0,
                            "dmErr": 1.0,
                            "rm": 10.0,
                            "rmErr": 1.0,
                            "sn": 100.0,
                            "flux": 25.0
                        }
                    }
                }
            ]
        }
    }


PLOT_CONTAINER_QUERY = """
query (
    $pulsar: String!
    $mainProject: String
    $projectShort: String
    $minimumNsubs: Boolean
    $maximumNsubs: Boolean
    $obsNchan: Int
    $obsNpol: Int
) {
    toa(
        pulsar: $pulsar
        mainProject: $mainProject
        projectShort: $projectShort
        minimumNsubs: $minimumNsubs
        maximumNsubs: $maximumNsubs
        obsNchan: $obsNchan
        obsNpol: $obsNpol
    ) {
    allProjects
    allNchans
    edges {
        node {
            observation {
                duration
                utcStart
                beam
                band
            }
            project {
                short
            }
            obsNchan
            minimumNsubs
            maximumNsubs
            dmCorrected
            id
            mjd
            dayOfYear
            binaryOrbitalPhase
            residualSec
            residualSecErr
            residualPhase
            residualPhaseErr
            }
        }
    }
}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_plot_container_query():
    client, user, _, _, _, template, pipeline_run, _, _ = setup_query_test()
    client.authenticate(user)
    for toa_file, nchan in TOA_FILES:
        if "molonglo" in toa_file:
            project = "MONSPSR_TIMING"
        else:
            project = "PTA"
        upload_toa_files(pipeline_run, project, nchan, template, toa_file)

    response = client.execute(
        PLOT_CONTAINER_QUERY,
        variables={
            "pulsar": "J0125-2327",
            "mainProject": "MeerTIME",
            "projectShort": "PTA",
            "minimumNsubs": True,
            "maximumNsubs": False,
            "obsNchan": 1,
            "obsNpol": 1,
        }
    )
    assert not response.errors
    print(json.dumps(response.data, indent=4))
    assert response.data == {
        "toa": {
            "allProjects": [
                "PTA"
            ],
            "allNchans": [
                1,
                4,
                16
            ],
            "edges": [
                {
                    "node": {
                        "observation": {
                            "duration": 263.99999999999994,
                            "utcStart": "2019-04-23T06:11:30+00:00",
                            "beam": 1,
                            "band": "LBAND"
                        },
                        "project": {
                            "short": "PTA"
                        },
                        "obsNchan": 1,
                        "minimumNsubs": True,
                        "maximumNsubs": False,
                        "dmCorrected": False,
                        "id": "VG9hTm9kZTo4MQ==",
                        "mjd": "58916.285422152018",
                        "dayOfYear": None,
                        "binaryOrbitalPhase": None,
                        "residualSec": None,
                        "residualSecErr": None,
                        "residualPhase": None,
                        "residualPhaseErr": None
                    }
                }
            ]
        }
    }


SINGLE_OBSERVATION_QUERY = """
query {
    pulsarFoldResult (
        pulsar: "J0125-2327",
        utcStart: "2020-07-10-05:07:28"
        beam: 2
    ) {
        edges {
            node {
                observation {
                    calibration {
                        id
                        idInt
                    }
                    beam
                    utcStart
                    obsType
                    project {
                        id
                        short
                        code
                        mainProject {
                            name
                        }
                    }
                    frequency
                    bandwidth
                    raj
                    decj
                    duration
                    foldNbin
                    foldNchan
                    foldTsubint
                    nant
                }
                pipelineRun {
                    dm
                    rm
                    sn
                }
                images {
                    edges {
                        node {
                            image
                            cleaned
                            imageType
                            resolution
                            url
                        }
                    }
                }
            }
        }
    }
}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_single_observation_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute(SINGLE_OBSERVATION_QUERY)
    assert not response.errors
    print(json.dumps(response.data, indent=4))
    assert response.data == {
        "pulsarFoldResult": {
            "edges": [
                {
                    "node": {
                        "observation": {
                            "calibration": {
                                "id": "Q2FsaWJyYXRpb25Ob2RlOjQy",
                                "idInt": 42
                            },
                            "beam": 2,
                            "utcStart": "2020-07-10T05:07:28+00:00",
                            "obsType": "FOLD",
                            "project": {
                                "id": "UHJvamVjdE5vZGU6MjY=",
                                "short": "PTA",
                                "code": "SCI-20180516-MB-05",
                                "mainProject": {
                                    "name": "MeerTIME"
                                }
                            },
                            "frequency": 815.734375,
                            "bandwidth": 544.0,
                            "raj": "01:25:01.0595040",
                            "decj": "-23:27:08.184197",
                            "duration": 1023.2854023529411,
                            "foldNbin": 1024,
                            "foldNchan": 1024,
                            "foldTsubint": 8,
                            "nant": 28
                        },
                        "pipelineRun": {
                            "dm": 20.0,
                            "rm": 10.0,
                            "sn": 100.0
                        },
                        "images": {
                            "edges": []
                        }
                    }
                }
            ]
        }
    }


SEARCH_QUERY = """
query {
    observationSummary(
        pulsar_Name: "All"
        obsType: "search"
        calibration_Id: "All"
        mainProject: "MeerTIME"
        project_Short: "All"
        band: "All"
    ) {
    edges {
        node {
            observations
            pulsars
            observationHours
            }
        }
    }
pulsarSearchSummary(
    mainProject: "MeerTIME"
    project: "All"
    band: "All"
    first: 1
) {
    edges {
        node {
            pulsar {
                name
            }
            latestObservation
            firstObservation
            allProjects
            mostCommonProject
            timespan
            numberOfObservations
            lastIntegrationMinutes
            totalIntegrationHours
            }
        }
    }
}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_search_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute(SEARCH_QUERY)
    assert not response.errors
    print(json.dumps(response.data, indent=4))
    assert response.data == {
        "observationSummary": {
            "edges": [
                {
                    "node": {
                        "observations": 3,
                        "pulsars": 3,
                        "observationHours": 4
                    }
                }
            ]
        },
        "pulsarSearchSummary": {
            "edges": [
                {
                    "node": {
                        "pulsar": {
                            "name": "J1614+0737"
                        },
                        "latestObservation": "2023-08-01T18:21:59+00:00",
                        "firstObservation": "2023-08-01T18:21:59+00:00",
                        "allProjects": "TPA",
                        "mostCommonProject": "TPA",
                        "timespan": 1,
                        "numberOfObservations": 1,
                        "lastIntegrationMinutes": 2.0044833333333334,
                        "totalIntegrationHours": 0.03340805555555555
                    }
                }
            ]
        }
    }


SEARCH_DETAIL_QUERY = """
query {
    observationSummary(
        pulsar_Name: "OmegaCen1"
        obsType: "search"
        calibration_Id: "All"
        mainProject: "MeerTIME"
        project_Short: "All"
        band: "All"
    ) {
        edges {
            node {
                observations
                projects
                observationHours
                timespanDays
            }
        }
    }
    observation(
        pulsar_Name: ["OmegaCen1"]
        mainProject: "MeerTIME"
        obsType: "search"
        first: 1
    ) {
        edges {
            node {
                id
                utcStart
                project {
                    short
                }
                raj
                decj
                beam
                duration
                frequency
                nantEff
                filterbankNbit
                filterbankNpol
                filterbankNchan
                filterbankTsamp
                filterbankDm
            }
        }
    }
}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_search_details_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute(SEARCH_DETAIL_QUERY)
    assert not response.errors
    print(json.dumps(response.data, indent=4))
    assert response.data == {
        "observationSummary": {
            "edges": [
                {
                    "node": {
                        "observations": 1,
                        "projects": 1,
                        "observationHours": 3,
                        "timespanDays": 1
                    }
                }
            ]
        },
        "observation": {
            "edges": [
                {
                    "node": {
                        "id": "T2JzZXJ2YXRpb25Ob2RlOjUy",
                        "utcStart": "2023-06-27T11:37:31+00:00",
                        "project": {
                            "short": "GC"
                        },
                        "raj": "13:26:47.24",
                        "decj": "-47:28:46.5",
                        "beam": 1,
                        "duration": 14399.068999999645,
                        "frequency": 1283.89550781,
                        "nantEff": 41,
                        "filterbankNbit": 8,
                        "filterbankNpol": 4,
                        "filterbankNchan": 256,
                        "filterbankTsamp": 19.14,
                        "filterbankDm": 99.9
                    }
                }
            ]
        }
    }


SESSION_QUERY = """
query {{
    observationSummary (
        pulsar_Name: "All",
        obsType: "All",
        calibrationInt: {cal},
        mainProject: "All",
        project_Short: "All",
        band: "All",
    ) {{
        edges {{
            node {{
                observations
                projects
                pulsars
            }}
        }}
    }}
    calibration (
        id: {cal}
    ) {{
        edges {{
            node {{
                id
                idInt
                start
                end
                observations {{
                    edges {{
                        node {{
                            id
                            pulsar {{
                                name
                            }}
                            utcStart
                            beam
                            obsType
                            duration
                            frequency
                            project {{
                                short
                            }}
                            pulsarFoldResults {{
                                edges {{
                                    node {{
                                        images {{
                                            edges {{
                                                node {{
                                                    url
                                                    imageType
                                                    cleaned
                                                }}
                                            }}
                                        }}
                                        pipelineRun {{
                                            sn
                                            percentRfiZapped
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
}}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_query():
    client, user, _, _, _, _, _, _, cal = setup_query_test()
    client.authenticate(user)

    response = client.execute(SESSION_QUERY.format(cal=cal.id))
    assert not response.errors
    assert len(response.data["calibration"]["edges"]) > 0
    assert len(response.data["observationSummary"]["edges"]) > 0
    print(json.dumps(response.data, indent=4))
    assert response.data == {
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
                        "id": "Q2FsaWJyYXRpb25Ob2RlOjYx",
                        "idInt": 61,
                        "start": "2019-04-23T06:11:30+00:00",
                        "end": "2019-04-23T06:11:30+00:00",
                        "observations": {
                            "edges": [
                                {
                                    "node": {
                                        "id": "T2JzZXJ2YXRpb25Ob2RlOjYx",
                                        "pulsar": {
                                            "name": "J0125-2327"
                                        },
                                        "utcStart": "2019-04-23T06:11:30+00:00",
                                        "beam": 1,
                                        "obsType": "FOLD",
                                        "duration": 263.99999999999994,
                                        "frequency": 1283.58203125,
                                        "project": {
                                            "short": "PTA"
                                        },
                                        "pulsarFoldResults": {
                                            "edges": [
                                                {
                                                    "node": {
                                                        "images": {
                                                            "edges": []
                                                        },
                                                        "pipelineRun": {
                                                            "sn": 100.0,
                                                            "percentRfiZapped": 10.0
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


SESSION_LIST_QUERY = """
query {
    calibration (
        first: 1
    ) {
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


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_list_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute(SESSION_LIST_QUERY)
    assert not response.errors
    assert response.data == {
        "calibration": {
            "edges": [
                {
                    "node": {
                        "id": "Q2FsaWJyYXRpb25Ob2RlOjY0",
                        "idInt": 64,
                        "start": "2023-08-01T18:21:59+00:00",
                        "end": "2023-08-01T18:21:59+00:00",
                        "allProjects": "TPA",
                        "nObservations": 1,
                        "nAntMin": 31,
                        "nAntMax": 31,
                        "totalIntegrationTimeSeconds": 120.26899999999999
                    }
                }
            ]
        }
    }


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_toa_uploads():
    _, _, _, _, _, template, pipeline_run, _, _ = setup_query_test()
    for toa_file, nchan in TOA_FILES:
        if "molonglo" in toa_file:
            project = "MONSPSR_TIMING"
        else:
            project = "PTA"
        upload_toa_files(pipeline_run, project, nchan, template, toa_file)


# Query used by the command `psrdb observation list`
OBSERVATION_LIST_QUERY = """
query observationList(
        $pulsar_Name: [String]
        $telescope_Name: String
        $project_Id: Int
        $project_Short: String
        $mainProject: String
        $utcStartGte: String
        $utcStartLte: String
        $obsType: String
    ) {
    observation (
        pulsar_Name: $pulsar_Name
        telescope_Name: $telescope_Name
        project_Id: $project_Id
        project_Short: $project_Short
        mainProject: $mainProject
        utcStartGte: $utcStartGte
        utcStartLte: $utcStartLte
        obsType: $obsType
    ) {
        edges {
            node {
                id
                pulsar {
                    name
                }
                calibration {
                    id
                    location
                }
                telescope {
                    name
                }
                project {
                    code
                    short
                }
                utcStart
                beam
                band
                duration
                foldNchan
                foldNbin
                modeDuration
            }
        }
    }
}
"""


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_observation_mode_duration():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy", email="slayer@sunnydail.com")
    client.authenticate(user)

    # Set up some observations
    telescope, project, ephemeris, template = create_basic_data()
    # "duration": 255.4990582429906
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"), telescope, template
    )
    # "duration": 263.99999999999994,
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"), telescope, template
    )

    response = client.execute(
        OBSERVATION_LIST_QUERY,
        variables={
            "pulsar_Name": None,
            "telescope_Name": None,
            "project_Id": None,
            "project_Short": None,
            "mainProject": None,
            "utcStartGte": None,
            "utcStartLte": None,
            "obsType": None,
        },
    )
    assert not response.errors
    # Should round to 256
    assert response.data["observation"]["edges"][0]["node"]["modeDuration"] == 256

    # Add two more observations and check it still rounds to the lower mode on a draw
    # "duration": 1039.9999999999998,
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"), telescope, template
    )
    # "duration": 1023.2854023529411,
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"), telescope, template
    )
    response = client.execute(
        OBSERVATION_LIST_QUERY,
        variables={
            "pulsar_Name": None,
            "telescope_Name": None,
            "project_Id": None,
            "project_Short": None,
            "mainProject": None,
            "utcStartGte": None,
            "utcStartLte": None,
            "obsType": None,
        },
    )
    assert not response.errors
    # Should round to 256
    assert response.data["observation"]["edges"][0]["node"]["modeDuration"] == 256

    # Add one more obs and it will get the new higher mode
    # "duration": 1023.2854023529411,
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"), telescope, template
    )
    response = client.execute(
        OBSERVATION_LIST_QUERY,
        variables={
            "pulsar_Name": None,
            "telescope_Name": None,
            "project_Id": None,
            "project_Short": None,
            "mainProject": None,
            "utcStartGte": None,
            "utcStartLte": None,
            "obsType": None,
        },
    )
    assert not response.errors
    assert response.data["observation"]["edges"][0]["node"]["modeDuration"] == 1024

    # Add 4 obs of a different pulsar and 4 obs of a different main project to ensure the filters work
    # J0437-4715 3 more times (already added once)
    # "duration": 255.4990582429906
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"), telescope, template
    )
    # Molonglo obs of same pulsar J0125-2327
    # "duration": 455.0798950400001,
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "molongolo_J0125-2327.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "molongolo_J0125-2327.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "molongolo_J0125-2327.json"), telescope, template
    )
    create_observation_pipeline_run_toa(
        os.path.join(TEST_DATA_DIR, "molongolo_J0125-2327.json"), telescope, template
    )
    response = client.execute(
        OBSERVATION_LIST_QUERY,
        variables={
            "pulsar_Name": ["J0125-2327"],
            "telescope_Name": None,
            "project_Id": None,
            "project_Short": None,
            "mainProject": "MeerTIME",
            "utcStartGte": None,
            "utcStartLte": None,
            "obsType": None,
        },
    )
    assert not response.errors
    assert response.data["observation"]["edges"][0]["node"]["modeDuration"] == 1024
