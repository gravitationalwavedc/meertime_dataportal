import json
import os

from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase

from dataportal.models import Badge
from dataportal.tests.testing_utils import (
    TEST_DATA_DIR,
    create_basic_data,
    create_observation_pipeline_run_toa,
    setup_query_test,
    upload_toa_files,
)
from utils.tests.test_toa import TOA_FILES

User = get_user_model()


class FrontendQueriesTestCase(GraphQLTestCase):
    """Test cases for frontend GraphQL queries"""

    # Define all GraphQL queries
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

    PLOT_CONTAINER_QUERY = """
    query (
        $pulsar: String!
        $mainProject: String
        $projectShort: String
        $nsubType: String
        $obsNchan: Int
        $obsNpol: Int
    ) {
        toa(
            pulsar: $pulsar
            mainProject: $mainProject
            projectShort: $projectShort
            nsubType: $nsubType
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
                nsubType
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

    TOA_EXCLUDE_BADGES_QUERY = """
    query toaBadgesExcluded (
        $pulsar: String
        $mainProject: String
        $projectShort: String
        $nsubType: String
        $obsNchan: Int
        $obsNpol: Int
        $excludeBadges: [String]
        $minimumSNR: Float
    ) {
        toa(
            pulsar: $pulsar
            mainProject: $mainProject
            projectShort: $projectShort
            nsubType: $nsubType
            obsNchan: $obsNchan
            obsNpol: $obsNpol
            excludeBadges: $excludeBadges
            minimumSNR: $minimumSNR
        ) {
            totalBadgeExcludedToas
            edges {
                node {
                    id
                }
            }
        }
    }
    """

    def setUp(self):
        """Setup basic test environment."""
        # Call setup_query_test once for all tests and store results as instance attributes
        # GraphQLTestCase provides self.client, so we ignore the client returned by setup_query_test
        (
            _,
            self.user,
            self.telescope,
            self.project,
            self.ephemeris,
            self.template,
            self.pipeline_run,
            self.observation,
            self.cal,
        ) = setup_query_test()

        # Force login with the user from setup_query_test
        self.client.force_login(self.user)

    def test_pulsar_fold_summary_query_with_token(self):
        """Test the pulsar fold summary query with an authenticated user."""
        # User is already logged in from setUp, just execute the query
        response = self.query(self.FOLD_SUMMARY_QUERY)

        # Parse the response content and check for errors
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check the response data
        self.assertEqual(content["data"]["pulsarFoldSummary"]["totalObservations"], 1)
        self.assertEqual(content["data"]["pulsarFoldSummary"]["totalPulsars"], 1)
        self.assertEqual(content["data"]["pulsarFoldSummary"]["totalObservationTime"], 0.1)
        self.assertEqual(content["data"]["pulsarFoldSummary"]["totalProjectTime"], 0)

        # Check the node data
        node = content["data"]["pulsarFoldSummary"]["edges"][0]["node"]
        self.assertEqual(node["pulsar"]["name"], "J0437-4715")
        self.assertEqual(node["latestObservation"], "2023-04-17T15:08:35+00:00")
        self.assertEqual(node["firstObservation"], "2023-04-17T15:08:35+00:00")
        self.assertEqual(node["mostCommonProject"], "PTA")
        self.assertEqual(node["timespan"], 1)
        self.assertEqual(node["numberOfObservations"], 1)
        self.assertAlmostEqual(node["totalIntegrationHours"], 0.07097196062305294)
        self.assertAlmostEqual(node["avgSnPipe"], 108.35924627749955)
        self.assertEqual(node["highestSn"], 100.0)
        self.assertEqual(node["lastSn"], 100.0)
        self.assertAlmostEqual(node["lastIntegrationMinutes"], 4.258317637383176)

    def test_fold_query(self):
        """Test fold query with different band parameters."""
        # User is already logged in from setUp, just execute the queries

        # Test with band="All"
        response = self.query(self.FOLD_QUERY.format(band="All"))
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check the response data for band="All"
        self.assertEqual(content["data"]["observationSummary"]["edges"][0]["node"]["observations"], 3)
        self.assertEqual(content["data"]["observationSummary"]["edges"][0]["node"]["pulsars"], 1)
        self.assertEqual(content["data"]["observationSummary"]["edges"][0]["node"]["observationHours"], 0)

        # Check pulsarFoldSummary
        node = content["data"]["pulsarFoldSummary"]["edges"][0]["node"]
        self.assertEqual(node["pulsar"]["name"], "J0437-4715")
        self.assertEqual(node["latestObservation"], "2023-04-17T15:08:35+00:00")
        self.assertEqual(node["latestObservationBeam"], 1)

        # Test with band="UHF"
        response = self.query(self.FOLD_QUERY.format(band="UHF"))
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check the response data for band="UHF"
        self.assertEqual(content["data"]["observationSummary"]["edges"][0]["node"]["observations"], 1)
        self.assertEqual(content["data"]["observationSummary"]["edges"][0]["node"]["pulsars"], 1)

        # Check pulsarFoldSummary for UHF band
        node = content["data"]["pulsarFoldSummary"]["edges"][0]["node"]
        self.assertEqual(node["pulsar"]["name"], "J0125-2327")
        self.assertEqual(node["latestObservation"], "2020-07-10T05:07:28+00:00")
        self.assertEqual(node["latestObservationBeam"], 2)

    def test_fold_detail_query(self):
        """Test the fold detail query."""
        # User is already logged in from setUp, just execute the query
        response = self.query(self.FOLD_DETAIL_QUERY)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check observation summary
        obs_summary = content["data"]["observationSummary"]["edges"][0]["node"]
        self.assertEqual(obs_summary["observations"], 3)
        self.assertEqual(obs_summary["observationHours"], 0)
        self.assertEqual(obs_summary["projects"], 1)
        self.assertEqual(obs_summary["pulsars"], 1)
        self.assertAlmostEqual(obs_summary["estimatedDiskSpaceGb"], 1.0766774425551469)

        # Remove variable parts that can change between test runs
        fold_result = content["data"]["pulsarFoldResult"]
        if "residualEphemeris" in fold_result and "createdAt" in fold_result["residualEphemeris"]:
            del fold_result["residualEphemeris"]["createdAt"]

        if "edges" in fold_result and len(fold_result["edges"]) > 0:
            observation = fold_result["edges"][0]["node"]["observation"]
            if "id" in observation:
                del observation["id"]
            if "calibration" in observation and "idInt" in observation["calibration"]:
                del observation["calibration"]["idInt"]

    def test_plot_container_query(self):
        """Test the plot container query."""
        # Upload TOA files for testing using instance attributes from setUp
        for toa_file, nchan in TOA_FILES:
            if "molonglo" in toa_file:
                project = "MONSPSR_TIMING"
            else:
                project = "PTA"
            upload_toa_files(self.pipeline_run, project, nchan, self.template, toa_file)

        # Execute the query
        response = self.query(
            self.PLOT_CONTAINER_QUERY,
            variables={
                "pulsar": "J0125-2327",
                "mainProject": "MeerTIME",
                "projectShort": "PTA",
                "nsubType": "1",
                "obsNchan": 1,
                "obsNpol": 1,
            },
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check the response data
        toa_data = content["data"]["toa"]
        self.assertEqual(toa_data["allProjects"], ["PTA"])
        self.assertEqual(toa_data["allNchans"], [1, 4, 16])

        # Check first node (removing variable ID)
        node = toa_data["edges"][0]["node"]
        if "id" in node:
            del node["id"]

        # Check observation details
        self.assertEqual(node["observation"]["duration"], 263.99999999999994)
        self.assertEqual(node["observation"]["utcStart"], "2019-04-23T06:11:30+00:00")
        self.assertEqual(node["observation"]["beam"], 1)
        self.assertEqual(node["observation"]["band"], "LBAND")
        self.assertEqual(node["project"]["short"], "PTA")
        self.assertEqual(node["obsNchan"], 1)
        self.assertEqual(node["nsubType"], "1")
        self.assertEqual(node["dmCorrected"], False)
        self.assertEqual(node["mjd"], "58916.285422152018")

    def test_single_observation_query(self):
        """Test the single observation query."""
        # User is already logged in from setUp, just execute the query
        response = self.query(self.SINGLE_OBSERVATION_QUERY)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Extract the node and remove variable parts
        result = content["data"]["pulsarFoldResult"]["edges"][0]["node"]
        if "calibration" in result["observation"]:
            if "id" in result["observation"]["calibration"]:
                del result["observation"]["calibration"]["id"]
            if "idInt" in result["observation"]["calibration"]:
                del result["observation"]["calibration"]["idInt"]

        if "project" in result["observation"] and "id" in result["observation"]["project"]:
            del result["observation"]["project"]["id"]

        # Check observation details
        observation = result["observation"]
        self.assertEqual(observation["beam"], 2)
        self.assertEqual(observation["utcStart"], "2020-07-10T05:07:28+00:00")
        self.assertEqual(observation["obsType"], "FOLD")
        self.assertEqual(observation["project"]["short"], "PTA")
        self.assertEqual(observation["project"]["code"], "SCI-20180516-MB-05")
        self.assertEqual(observation["project"]["mainProject"]["name"], "MeerTIME")

    def test_search_query(self):
        """Test the search query."""
        # User is already logged in from setUp, just execute the query
        response = self.query(self.SEARCH_QUERY)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check observation summary
        obs_summary = content["data"]["observationSummary"]["edges"][0]["node"]
        self.assertEqual(obs_summary["observations"], 3)
        self.assertEqual(obs_summary["pulsars"], 3)
        self.assertEqual(obs_summary["observationHours"], 4)

        # Check search summary
        search_summary = content["data"]["pulsarSearchSummary"]["edges"][0]["node"]
        self.assertEqual(search_summary["pulsar"]["name"], "J1614+0737")
        self.assertEqual(search_summary["latestObservation"], "2023-08-01T18:21:59+00:00")
        self.assertEqual(search_summary["firstObservation"], "2023-08-01T18:21:59+00:00")
        self.assertEqual(search_summary["allProjects"], "TPA")
        self.assertEqual(search_summary["mostCommonProject"], "TPA")

    def test_search_details_query(self):
        """Test the search details query."""
        # User is already logged in from setUp, just execute the query
        response = self.query(self.SEARCH_DETAIL_QUERY)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check observation summary
        obs_summary = content["data"]["observationSummary"]["edges"][0]["node"]
        self.assertEqual(obs_summary["observations"], 1)
        self.assertEqual(obs_summary["projects"], 1)
        self.assertEqual(obs_summary["observationHours"], 3)
        self.assertEqual(obs_summary["timespanDays"], 1)

        # Check observation details (removing variable ID)
        observation = content["data"]["observation"]["edges"][0]["node"]
        if "id" in observation:
            del observation["id"]

        self.assertEqual(observation["utcStart"], "2023-06-27T11:37:31+00:00")
        self.assertEqual(observation["project"]["short"], "GC")
        self.assertEqual(observation["raj"], "13:26:47.24")
        self.assertEqual(observation["decj"], "-47:28:46.5")

    def test_session_query(self):
        """Test the session query."""
        # User is already logged in from setUp and self.cal is available from setUp
        response = self.query(self.SESSION_QUERY.format(cal=self.cal.id))
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check if edges exist in the response
        self.assertTrue(len(content["data"]["calibration"]["edges"]) > 0)
        self.assertTrue(len(content["data"]["observationSummary"]["edges"]) > 0)

        # Remove variable IDs
        calibration = content["data"]["calibration"]["edges"][0]["node"]
        if "id" in calibration:
            del calibration["id"]
        if "idInt" in calibration:
            del calibration["idInt"]

        if len(calibration["observations"]["edges"]) > 0:
            observation = calibration["observations"]["edges"][0]["node"]
            if "id" in observation:
                del observation["id"]

        # Check calibration details
        self.assertEqual(calibration["start"], "2019-04-23T06:11:30+00:00")
        self.assertEqual(calibration["end"], "2019-04-23T06:11:30+00:00")

        # Check observation summary
        obs_summary = content["data"]["observationSummary"]["edges"][0]["node"]
        self.assertEqual(obs_summary["observations"], 1)
        self.assertEqual(obs_summary["projects"], 1)
        self.assertEqual(obs_summary["pulsars"], 1)

    def test_session_list_query(self):
        """Test the session list query."""
        # User is already logged in from setUp, just execute the query
        response = self.query(self.SESSION_LIST_QUERY)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check if edges exist in the response
        self.assertTrue(len(content["data"]["calibration"]["edges"]) > 0)

        # Remove variable IDs
        calibration = content["data"]["calibration"]["edges"][0]["node"]
        if "id" in calibration:
            del calibration["id"]
        if "idInt" in calibration:
            del calibration["idInt"]

        # Check calibration details
        self.assertEqual(calibration["start"], "2023-08-01T18:21:59+00:00")
        self.assertEqual(calibration["end"], "2023-08-01T18:21:59+00:00")
        self.assertEqual(calibration["allProjects"], "TPA")
        self.assertEqual(calibration["nObservations"], 1)
        self.assertEqual(calibration["nAntMin"], 31)
        self.assertEqual(calibration["nAntMax"], 31)
        self.assertAlmostEqual(calibration["totalIntegrationTimeSeconds"], 120.26899999999999)

    def test_toa_uploads(self):
        """Test TOA file uploads."""
        # Use self.template and self.pipeline_run from setUp
        for toa_file, nchan in TOA_FILES:
            if "molonglo" in toa_file:
                project = "MONSPSR_TIMING"
            else:
                project = "PTA"
            upload_toa_files(self.pipeline_run, project, nchan, self.template, toa_file)

        # This test is successful if no exceptions are raised

    def test_observation_mode_duration(self):
        """Test observation mode duration calculations."""
        # This test specifically needs a fresh set of observations to test mode duration
        # but we can use the client from the base class

        from dataportal.models import Ephemeris, Project, Pulsar, Telescope, Template

        Pulsar.objects.all().delete()  # Clear existing pulsars
        Telescope.objects.all().delete()  # Clear existing telescopes
        Project.objects.all().delete()  # Clear existing projects
        Ephemeris.objects.all().delete()  # Clear existing ephemerides
        Template.objects.all().delete()  # Clear existing templates

        # Set up some observations using create_basic_data
        telescope, project, ephemeris, template = create_basic_data()
        # "duration": 255.4990582429906
        create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"),
            telescope,
            template,
        )
        # "duration": 263.99999999999994,
        create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"),
            telescope,
            template,
        )

        # Execute query using self.query (which uses self.client)
        response = self.query(
            self.OBSERVATION_LIST_QUERY,
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
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Should round to 256
        self.assertEqual(content["data"]["observation"]["edges"][0]["node"]["modeDuration"], 256)

        # Add two more observations and check it still rounds to the lower mode on a draw
        create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"),
            telescope,
            template,
        )
        create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
            telescope,
            template,
        )

        response = self.query(
            self.OBSERVATION_LIST_QUERY,
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
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Should still be 256
        self.assertEqual(content["data"]["observation"]["edges"][0]["node"]["modeDuration"], 256)

        # Add one more obs and it will get the new higher mode
        create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
            telescope,
            template,
        )

        response = self.query(
            self.OBSERVATION_LIST_QUERY,
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
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Should now be 1024
        self.assertEqual(content["data"]["observation"]["edges"][0]["node"]["modeDuration"], 1024)

        # Add additional observations for filtering tests
        for _ in range(3):
            create_observation_pipeline_run_toa(
                os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"),
                telescope,
                template,
            )

        for _ in range(4):
            create_observation_pipeline_run_toa(
                os.path.join(TEST_DATA_DIR, "molongolo_J0125-2327.json"), telescope, template
            )

        # Test filtered query
        response = self.query(
            self.OBSERVATION_LIST_QUERY,
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
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        self.assertEqual(content["data"]["observation"]["edges"][0]["node"]["modeDuration"], 1024)

    def test_total_badge_excluded_toas(self):
        """Test excluding TOAs with badges."""
        # This test specifically needs to create its own data with badges
        # but we can use the client from the base class

        from dataportal.models import Pulsar, Telescope

        Pulsar.objects.all().delete()  # Clear existing pulsars
        Telescope.objects.all().delete()  # Clear existing telescopes

        # Set up basic data
        telescope, project, ephemeris, template = create_basic_data()

        # Create badge and pipeline runs
        obs1, cal1, pr1 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"),
            telescope,
            template,
            make_toas=False,
        )
        dm_badge, created = Badge.objects.get_or_create(
            name="DM Drift",
            description="The DM has drifted away from the median DM of the pulsar enough to cause a dispersion of three profile bins",
        )
        pr1.badges.add(dm_badge)

        obs2, cal2, pr2 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"),
            telescope,
            template,
            make_toas=False,
        )

        # Upload TOA files with various parameters
        upload_toa_files(
            pr1,
            "PTA",
            16,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim",
            ),
        )

        # Different nsub types
        upload_toa_files(
            pr1,
            "PTA",
            16,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim",
            ),
            nsub_type="max",
        )
        upload_toa_files(
            pr1,
            "PTA",
            16,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim",
            ),
            nsub_type="all",
        )
        upload_toa_files(
            pr1,
            "PTA",
            16,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim",
            ),
            nsub_type="mode",
        )

        # Redundant toa
        upload_toa_files(
            pr1,
            "PTA",
            16,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim",
            ),
            nsub_type="1",
        )
        upload_toa_files(
            pr1,
            "PTA",
            16,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim",
            ),
        )

        # Different nchan
        upload_toa_files(
            pr1,
            "PTA",
            1,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.1ch1p1t.ar.tim",
            ),
        )

        # Different project
        upload_toa_files(
            pr1,
            "TPA",
            16,
            template,
            os.path.join(
                TEST_DATA_DIR,
                "timing_files/J0437-4715_2023-10-22-04:41:07_zap.16ch1p1t.ar.tim",
            ),
        )

        # Execute query with badge exclusion using self.query (which uses self.client)
        response = self.query(
            self.TOA_EXCLUDE_BADGES_QUERY,
            variables={
                "pulsar": "J0437-4715",
                "mainProject": "MeerTIME",
                "projectShort": "PTA",
                "nsubType": "1",
                "modeNsubs": False,
                "obsNchan": 16,
                "obsNpol": 1,
                "excludeBadges": ["DM Drift"],
                "minimumSNR": 0,
            },
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        # Check that badges are excluded
        self.assertEqual(content["data"]["toa"]["totalBadgeExcludedToas"], 16)
        self.assertEqual(len(content["data"]["toa"]["edges"]), 0)
