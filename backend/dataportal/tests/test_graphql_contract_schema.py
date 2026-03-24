import json

from graphene_django.utils.testing import GraphQLTestCase

from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import setup_query_test


class GraphQLSchemaContractTestCase(GraphQLTestCase):
    """Lock GraphQL query argument names for key filter-heavy fields."""

    INTROSPECTION_QUERY = """
    query {
      __type(name: "Query") {
        fields {
          name
          args {
            name
          }
        }
      }
    }
    """

    def test_filter_query_argument_names_are_stable(self):
        response = self.query(self.INTROSPECTION_QUERY)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        fields = {
            field["name"]: {arg["name"] for arg in field["args"]} for field in content["data"]["__type"]["fields"]
        }

        self.assertEqual(
            fields["observation"],
            {
                "after",
                "before",
                "first",
                "incomplete",
                "last",
                "mainProject",
                "offset",
                "obsType",
                "project_Id",
                "project_Short",
                "pulsar_Name",
                "telescope_Name",
                "unprocessed",
                "utcStartGte",
                "utcStartLte",
            },
        )
        self.assertEqual(
            fields["observationSummary"],
            {
                "after",
                "band",
                "before",
                "calibrationInt",
                "calibration_Id",
                "first",
                "last",
                "mainProject",
                "offset",
                "obsType",
                "project_Id",
                "project_Short",
                "pulsar_Name",
            },
        )
        self.assertEqual(
            fields["pulsarFoldResult"],
            {
                "after",
                "beam",
                "before",
                "excludeBadges",
                "first",
                "last",
                "mainProject",
                "offset",
                "minimumSNR",
                "pulsar",
                "utcStart",
                "utcStartGte",
                "utcStartLte",
            },
        )
        self.assertEqual(
            fields["toa"],
            {
                "after",
                "before",
                "dmCorrected",
                "excludeBadges",
                "first",
                "last",
                "mainProject",
                "offset",
                "minimumSNR",
                "nsubType",
                "obsNchan",
                "obsNpol",
                "pipelineRunId",
                "projectShort",
                "pulsar",
                "utcStartGte",
                "utcStartLte",
            },
        )


class GraphQLRelayConnectionContractTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    """Verify key Relay connection response contract fields exist and are populated."""

    @classmethod
    def setUpTestData(cls):
        (
            _,
            cls.user,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = setup_query_test()

    def setUp(self):
        self.client.force_login(self.user)

    def test_observation_connection_has_pageinfo_and_cursor(self):
        response = self.query(
            """
            query {
              observation(first: 2) {
                pageInfo {
                  hasNextPage
                  hasPreviousPage
                  startCursor
                  endCursor
                }
                edges {
                  cursor
                  node {
                    id
                  }
                }
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        connection = content["data"]["observation"]
        self.assertIn("pageInfo", connection)
        self.assertIn("edges", connection)
        self.assertGreater(len(connection["edges"]), 0)
        self.assertIsNotNone(connection["edges"][0]["cursor"])
        self.assertIsNotNone(connection["edges"][0]["node"]["id"])

    def test_pulsar_fold_result_connection_has_pageinfo_and_cursor(self):
        response = self.query(
            """
            query {
              pulsarFoldResult(pulsar: "J0125-2327", mainProject: "MeerTIME", first: 2) {
                pageInfo {
                  hasNextPage
                  hasPreviousPage
                  startCursor
                  endCursor
                }
                edges {
                  cursor
                  node {
                    observation {
                      id
                    }
                  }
                }
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        connection = content["data"]["pulsarFoldResult"]
        self.assertIn("pageInfo", connection)
        self.assertIn("edges", connection)
        self.assertGreater(len(connection["edges"]), 0)
        self.assertIsNotNone(connection["edges"][0]["cursor"])
        self.assertIsNotNone(connection["edges"][0]["node"]["observation"]["id"])

    def test_toa_connection_has_pageinfo_and_cursor(self):
        response = self.query(
            """
            query {
              toa(
                pulsar: "J0125-2327"
                mainProject: "MeerTIME"
                projectShort: ""
                nsubType: "1"
                obsNchan: 1
                first: 10
              ) {
                pageInfo {
                  hasNextPage
                  hasPreviousPage
                  startCursor
                  endCursor
                }
                edges {
                  cursor
                  node {
                    id
                  }
                }
                allProjects
                allNchans
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        connection = content["data"]["toa"]
        self.assertIn("pageInfo", connection)
        self.assertIn("edges", connection)
        self.assertIn("allProjects", connection)
        self.assertIn("allNchans", connection)
        self.assertGreater(len(connection["edges"]), 0)
        self.assertIsNotNone(connection["edges"][0]["cursor"])
        self.assertIsNotNone(connection["edges"][0]["node"]["id"])
