import json

from graphene_django.utils.testing import GraphQLTestCase

from dataportal.models import MainProject, Project, Telescope


class ProjectConfigurationQueryTest(GraphQLTestCase):
    QUERY = """
    query {
      projectConfiguration {
        edges {
          node {
            code
            short
            description
            isVisibleOnFrontend
            displayOrder
            bandOptions
            plotTypes
            allowDownloads
            showExtendedObservationFields
            observationBandOverride
            toaMetadataAvailable
            useForFoldingAssets
            mainProject {
              name
              telescope { name }
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        first_telescope = Telescope.objects.create(name="First Scope")
        first_main = MainProject.objects.create(name="First Programme", telescope=first_telescope)
        second_telescope = Telescope.objects.create(name="Second Scope")
        second_main = MainProject.objects.create(name="Second Programme", telescope=second_telescope)

        Project.objects.create(
            code="VISIBLE-LATE",
            short="LATE",
            description="Visible later",
            main_project=first_main,
            display_order=20,
            band_options=["LBAND", "UHF"],
            plot_types=["Timing Residuals", "S/N"],
            allow_downloads=False,
            show_extended_observation_fields=False,
            observation_band_override="UHF_NS",
            toa_metadata_available=False,
            use_for_folding_assets=False,
        )
        Project.objects.create(
            code="VISIBLE-FIRST",
            short="FIRST",
            main_project=second_main,
            display_order=10,
        )
        Project.objects.create(
            code="HIDDEN",
            short="HIDE",
            main_project=first_main,
            is_visible_on_frontend=False,
            display_order=5,
        )

    def test_project_configuration_is_public_visible_and_ordered(self):
        response = self.query(self.QUERY)
        content = json.loads(response.content)

        self.assertNotIn("errors", content)
        nodes = [edge["node"] for edge in content["data"]["projectConfiguration"]["edges"]]
        self.assertEqual([node["code"] for node in nodes], ["VISIBLE-FIRST", "VISIBLE-LATE"])
        self.assertEqual(nodes[0]["mainProject"]["name"], "Second Programme")
        self.assertEqual(nodes[0]["mainProject"]["telescope"]["name"], "Second Scope")

        configured = nodes[1]
        self.assertEqual(configured["bandOptions"], ["LBAND", "UHF"])
        self.assertEqual(configured["plotTypes"], ["Timing Residuals", "S/N"])
        self.assertFalse(configured["allowDownloads"])
        self.assertFalse(configured["showExtendedObservationFields"])
        self.assertEqual(configured["observationBandOverride"], "UHF_NS")
        self.assertFalse(configured["toaMetadataAvailable"])
        self.assertFalse(configured["useForFoldingAssets"])
