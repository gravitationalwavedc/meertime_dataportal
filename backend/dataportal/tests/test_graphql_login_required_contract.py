import json

from graphene_django.utils.testing import GraphQLTestCase

from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import create_pulsar_with_observations

LOGIN_REQUIRED_MESSAGE = "You must be logged in to perform this action"


class GraphQLLoginRequiredContractTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    """Ensure login_required fields stay restricted for anonymous users."""

    @classmethod
    def setUpTestData(cls):
        create_pulsar_with_observations()

    def assert_login_required_errors(self, content, expected_paths):
        self.assertIn("errors", content)

        for error in content["errors"]:
            self.assertEqual(error["message"], LOGIN_REQUIRED_MESSAGE)

        error_paths = {tuple(error.get("path", [])) for error in content["errors"] if "path" in error}
        for path in expected_paths:
            self.assertIn(path, error_paths)

    def test_anonymous_cannot_access_login_required_root_fields(self):
        response = self.query(
            """
            query {
              telescope(first: 1) { edges { node { id } } }
              project(first: 1) { edges { node { id } } }
              ephemeris(first: 1) { edges { node { id } } }
              template(first: 1) { edges { node { id } } }
              pipelineRun(first: 1) { edges { node { id } } }
              pipelineImage(first: 1) { edges { node { id } } }
              badge(first: 1) { edges { node { id } } }
              toa(first: 1) { edges { node { id } } }
            }
            """
        )
        content = json.loads(response.content)
        self.assert_login_required_errors(
            content,
            {
                ("telescope",),
                ("project",),
                ("ephemeris",),
                ("template",),
                ("pipelineRun",),
                ("pipelineImage",),
                ("badge",),
                ("toa",),
            },
        )
