from django.test import TestCase

from dataportal.admin import ProjectAdminForm
from dataportal.models import MainProject, Project, Telescope


class ProjectRuntimeConfigTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        telescope = Telescope.objects.create(name="Synthetic Scope")
        cls.main_project = MainProject.objects.create(name="Synthetic Programme", telescope=telescope)

    def test_runtime_configuration_defaults_preserve_existing_behaviour(self):
        project = Project.objects.create(code="SYNTHETIC", main_project=self.main_project)

        self.assertTrue(project.allow_downloads)
        self.assertTrue(project.show_extended_observation_fields)
        self.assertEqual(project.observation_band_override, "")
        self.assertTrue(project.toa_metadata_available)
        self.assertTrue(project.use_for_folding_assets)

    def test_runtime_configuration_accepts_alternative_values(self):
        project = Project.objects.create(
            code="SYNTHETIC-CONFIGURED",
            main_project=self.main_project,
            allow_downloads=False,
            show_extended_observation_fields=False,
            observation_band_override="UHF_NS",
            toa_metadata_available=False,
            use_for_folding_assets=False,
        )

        self.assertFalse(project.allow_downloads)
        self.assertFalse(project.show_extended_observation_fields)
        self.assertEqual(project.observation_band_override, "UHF_NS")
        self.assertFalse(project.toa_metadata_available)
        self.assertFalse(project.use_for_folding_assets)

    def test_runtime_configuration_is_available_in_admin(self):
        self.assertTrue(
            {
                "allow_downloads",
                "show_extended_observation_fields",
                "observation_band_override",
                "toa_metadata_available",
                "use_for_folding_assets",
            }.issubset(ProjectAdminForm.base_fields)
        )
