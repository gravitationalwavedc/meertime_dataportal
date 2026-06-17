"""
Tests for the `isEmbargoed` field on ObservationNode.

The field delegates to the existing `Observation.is_embargoed` property:
returns True if the observation is still under embargo, False otherwise.
"""

import json
import os
from datetime import timedelta

from django.utils import timezone
from graphene_django.utils.testing import GraphQLTestCase

from dataportal.models import (
    MainProject,
    Project,
    Pulsar,
)
from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import (
    TEST_DATA_DIR,
    create_basic_data,
    create_observation_pipeline_run_toa,
)

OBSERVATION_QUERY = """
query IsEmbargoedTest($pulsar: String!, $mainProject: String!) {
  pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject, first: 10) {
    edges {
      node {
        id
        observation {
          isEmbargoed
        }
      }
    }
  }
}
"""


class ObservationNodeIsEmbargoedTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    """GraphQL contract test for ObservationNode.isEmbargoed."""

    @classmethod
    def setUpTestData(cls):
        # create_basic_data returns (telescope, last-project, ephemeris, template);
        # the last project it creates is RelBin, so we look up PTA explicitly
        # — that matches the projectCode in the J0125-2327 fixture JSON.
        telescope, _, _, template = create_basic_data()

        main_project = MainProject.objects.get(name="MeerTIME")
        project = Project.objects.get(short="PTA", main_project=main_project)
        pulsar = Pulsar.objects.get(name="J0125-2327")

        json_file = os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json")

        # Embargoed observation: utc_start 30 days ago + 18-month embargo period -> still embargoed.
        obs_embargoed, _, _ = create_observation_pipeline_run_toa(json_file, telescope, template, make_toas=False)
        cls.embargoed_obs = obs_embargoed
        cls.embargoed_obs.project = project
        cls.embargoed_obs.utc_start = timezone.now() - timedelta(days=30)
        cls.embargoed_obs.save()

        # Public observation: utc_start 600 days ago + 18-month embargo period -> public.
        obs_public, _, _ = create_observation_pipeline_run_toa(json_file, telescope, template, make_toas=False)
        cls.public_obs = obs_public
        cls.public_obs.project = project
        cls.public_obs.utc_start = timezone.now() - timedelta(days=600)
        cls.public_obs.save()

        cls.pulsar = pulsar
        cls.main_project = "MeerTIME"

    def _query_edges(self):
        response = self.query(
            OBSERVATION_QUERY,
            variables={"pulsar": "J0125-2327", "mainProject": "MeerTIME"},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"GraphQL errors: {content}")

        edges = content["data"]["pulsarFoldResult"]["edges"]
        self.assertGreaterEqual(len(edges), 1, "Expected at least one fold result edge")
        return edges

    def _find_edge(self, edges, expected_embargoed):
        for edge in edges:
            if edge["node"]["observation"]["isEmbargoed"] is expected_embargoed:
                return edge
        raise AssertionError(f"No edge with isEmbargoed={expected_embargoed} found in {edges}")

    def test_embargoed_observation_returns_true(self):
        """isEmbargoed is True when the observation is still under embargo."""
        edges = self._query_edges()
        edge = self._find_edge(edges, True)
        self.assertTrue(edge["node"]["observation"]["isEmbargoed"])

    def test_public_observation_returns_false(self):
        """isEmbargoed is False when the embargo period has expired."""
        edges = self._query_edges()
        edge = self._find_edge(edges, False)
        self.assertFalse(edge["node"]["observation"]["isEmbargoed"])
