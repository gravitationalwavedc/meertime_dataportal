from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from dataportal.admin import ProjectAdminForm
from dataportal.models import Calibration, MainProject, Observation, Project, Pulsar, Telescope


class ProjectRuntimeConfigTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        telescope = Telescope.objects.create(name="Synthetic Scope")
        cls.telescope = telescope
        cls.main_project = MainProject.objects.create(name="Synthetic Programme", telescope=telescope)
        cls.pulsar = Pulsar.objects.create(name="J0000+0000")
        cls.calibration = Calibration.objects.create(schedule_block_id="cal-01", calibration_type="pre")

    def create_observation(self, project, frequency=1400.0, bandwidth=400.0):
        with patch("dataportal.signals.ObservationSummary.update_or_create"):
            return Observation.objects.create(
                pulsar=self.pulsar,
                telescope=self.telescope,
                project=project,
                calibration=self.calibration,
                utc_start=timezone.now(),
                frequency=frequency,
                bandwidth=bandwidth,
                nchan=1024,
                beam=1,
                nant=32,
                nant_eff=30,
                npol=2,
                obs_type="fold",
                raj="00:00:00",
                decj="-00:00:00",
                duration=600.0,
                nbit=8,
                tsamp=0.001,
            )

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

    def test_observation_band_uses_configured_project_override(self):
        project = Project.objects.create(
            code="SYNTHETIC-OVERRIDE",
            main_project=self.main_project,
            observation_band_override="UHF_NS",
        )

        observation = self.create_observation(project)

        self.assertEqual(observation.band, "UHF_NS")

    def test_observation_band_is_calculated_without_project_override(self):
        project = Project.objects.create(code="SYNTHETIC-CALCULATED", main_project=self.main_project)

        observation = self.create_observation(project, frequency=1283.5)

        self.assertEqual(observation.band, "LBAND")
