import os
import json
import copy
import pytest
from dataportal.tests.testing_utils import setup_query_test, upload_toa_files, TEST_DATA_DIR, CYPRESS_FIXTURE_DIR
from utils.tests.test_toa import TOA_FILES



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

    # with open(os.path.join(TEST_DATA_DIR, "pulsarFoldSummary.json"), 'w') as json_file:
    #     json.dump(response.data, json_file, indent=2)
    with open(os.path.join(TEST_DATA_DIR, "pulsarFoldSummary.json"), 'r') as file:
        expected = json.load(file)

    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)
    query = """
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
        pulsarFoldSummary(
            mainProject: "MeerTIME"
            project: "All"
            band: "{band}"
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

    response = client.execute(query.format(band="All"))
    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "foldQuery.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    with open(os.path.join(CYPRESS_FIXTURE_DIR, "foldQuery.json"), 'r') as file:
        expected = json.load(file)
    assert not response.errors
    assert response.data == expected["data"]

    response = client.execute(query.format(band="UHF"))
    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "foldQueryFewer.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    with open(os.path.join(CYPRESS_FIXTURE_DIR, "foldQueryFewer.json"), 'r') as file:
        expected = json.load(file)
    assert not response.errors
    assert response.data == expected["data"]


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_detail_query():
    client, user, telescope, project, ephemeris, template, pipeline_run, obs, cal = setup_query_test()
    client.authenticate(user)
    response = client.execute("""
        query {
            observationSummary(
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
            pulsarFoldResult(pulsar: "J0125-2327", mainProject: "MeerTIME") {
                residualEphemeris {
                    ephemerisData
                    createdAt
                }
                description
                toasLink
                allProjects
                edges {
                    node {
                        observation {
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
                            toas(
                                dmCorrected: false
                                minimumNsubs: true
                                obsNchan: 1
                            ) {
                            edges {
                                node {
                                    freqMhz
                                    length
                                    project {
                                        short
                                    }
                                    residual {
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
    """)

    assert not response.errors
    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "foldDetailQuery.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "foldDetailQueryNoEphem.json"), 'w') as json_file:
    #     response_copy = copy.deepcopy(response.data)
    #     test_out = copy.copy({"data": response_copy})
    #     del test_out["data"]["pulsarFoldResult"]["residualEphemeris"]
    #     json.dump(test_out, json_file, indent=2)
    with open(os.path.join(CYPRESS_FIXTURE_DIR, "foldDetailQuery.json"), 'r') as file:
        expected = json.load(file)["data"]
    del response.data["pulsarFoldResult"]["residualEphemeris"]["createdAt"]
    del expected["pulsarFoldResult"]["residualEphemeris"]["createdAt"]
    assert response.data == expected




@pytest.mark.django_db
@pytest.mark.enable_signals
def test_single_observation_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)
    response = client.execute("""
        query {
            pulsarFoldResult(pulsar: "J0125-2327", utcStart: "2020-07-10-05:07:28" beam: 2) {
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
    """)

    # with open(os.path.join(TEST_DATA_DIR, "singleObservationQuery.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "singleObservationQueryNoImages.json"), 'w') as json_file:
    #     response_copy = copy.copy(response.data)
    #     test_out = copy.copy({"data": response_copy})
    #     test_out["data"]["fileSingleList"] = {
    #         "edges": [
    #             {
    #                 "node": {
    #                     "path": "MeerKAT/SCI-20180516-MB-05/J0125-2327/2023-04-29-06:47:34/2/J0125-2327.FTS.ar",
    #                     "fileSize": "1GB"
    #                 }
    #             }
    #         ]
    #     }
    #     json.dump(test_out, json_file, indent=2)
    with open(os.path.join(TEST_DATA_DIR, "singleObservationQuery.json"), 'r') as file:
        expected = json.load(file)["data"]
    assert not response.errors
    assert response.data == expected

@pytest.mark.django_db
@pytest.mark.enable_signals
def test_search_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)
    response = client.execute("""
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
    """)

    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "searchQuery.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    with open(os.path.join(CYPRESS_FIXTURE_DIR, "searchQuery.json"), 'r') as file:
        expected = json.load(file)["data"]
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_search_details_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)
    response = client.execute("""
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
    """)
    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "searchDetailQuery.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    with open(os.path.join(CYPRESS_FIXTURE_DIR, "searchDetailQuery.json"), 'r') as file:
        expected = json.load(file)["data"]
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_query():
    client, user, telescope, project, ephemeris, template, pipeline_run, obs, cal = setup_query_test()
    client.authenticate(user)
    response = client.execute("""
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
            calibration (id: {cal}) {{
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
    """.format(cal=cal.id))
    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "sessionQuery.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    with open(os.path.join(CYPRESS_FIXTURE_DIR, "sessionQuery.json"), 'r') as file:
        expected = json.load(file)["data"]
    assert not response.errors
    assert len(response.data["calibration"]["edges"]) > 0
    assert len(response.data["observationSummary"]["edges"]) > 0
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_list_query():
    client, user = setup_query_test()[:2]
    client.authenticate(user)

    response = client.execute("""
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
    """)

    # with open(os.path.join(CYPRESS_FIXTURE_DIR, "sessionListQuery.json"), 'w') as json_file:
    #     json.dump({"data": response.data}, json_file, indent=2)
    with open(os.path.join(CYPRESS_FIXTURE_DIR, "sessionListQuery.json"), 'r') as file:
        expected = json.load(file)["data"]
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_toa_uploads():
    client, user, telescope, project, ephemeris, template, pipeline_run, obs, cal = setup_query_test()
    for toa_file in TOA_FILES:
        upload_toa_files(pipeline_run, "PTA", template, toa_file)
