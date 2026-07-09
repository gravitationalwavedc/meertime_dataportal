import json
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from dataportal.admin import ProjectAdminForm
from dataportal.models import (
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    PipelineRun,
    Project,
    Pulsar,
    Telescope,
    Template,
    Toa,
)


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

    def create_toa_dependencies(self, project):
        now = timezone.now()
        ephemeris = Ephemeris.objects.create(
            pulsar=self.pulsar,
            project=project,
            ephemeris_data=json.dumps({"DM": 12.3, "P0": 0.5}),
            p0=0.5,
            dm=12.3,
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1),
        )
        template = Template.objects.create(
            pulsar=self.pulsar,
            project=project,
            band="LBAND",
            template_hash=f"template-{project.short}",
        )
        observation = self.create_observation(project)
        Observation.objects.filter(pk=observation.pk).update(ephemeris=ephemeris, fold_nbin=128)
        observation.refresh_from_db()

        return PipelineRun.objects.create(
            observation=observation,
            ephemeris=ephemeris,
            template=template,
            pipeline_name="test",
            pipeline_version="1",
            created_by="tester",
            location="/tmp",
            job_state="Completed",
            sn=5.0,
            dm=12.3,
            percent_rfi_zapped=0.0,
        ), template

    def create_toa(self, project):
        pipeline_run, template = self.create_toa_dependencies(project)
        toa_line = "toa line\n"
        toa_dict = {
            "archive": "archive.ar",
            "freq_MHz": 1400.0,
            "mjd": "59000.123456789012",
            "mjd_err": 1.0,
            "telescope": "synthetic",
            "fe": "fe",
            "be": "be",
            "f": "f",
            "bw": 400,
            "tobs": 600,
            "tmplt": "template",
            "nbin": 128,
            "snr": 20.0,
            "nch": 16,
            "chan": 4,
            "rcvr": "receiver",
            "length": 30,
            "subint": 2,
        }

        with (
            patch(
                "dataportal.models.parse_ephemeris_file",
                return_value={
                    "P0": 0.5,
                    "DM": 12.3,
                    "START": (timezone.now() - timedelta(days=1)).isoformat(),
                    "FINISH": (timezone.now() + timedelta(days=1)).isoformat(),
                },
            ),
            patch("dataportal.models.toa_line_to_dict", return_value=toa_dict),
            patch("dataportal.models.toa_dict_to_line", return_value=toa_line.rstrip("\n")),
        ):
            return Toa.bulk_create(
                pipeline_run_id=pipeline_run.id,
                project_short=project.short,
                template_id=template.id,
                ephemeris_text="FAKE",
                toa_lines=[toa_line],
                dm_corrected=False,
                nsub_type="1",
                npol=2,
                nchan=16,
            )[0]

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

    def test_toa_metadata_is_stored_when_project_metadata_is_available(self):
        project = Project.objects.create(
            code="SYNTHETIC-TOA-METADATA",
            short="SYN-TOA-YES",
            main_project=self.main_project,
        )

        toa = self.create_toa(project)

        self.assertEqual(toa.nch, 16)
        self.assertEqual(toa.chan, 4)
        self.assertEqual(toa.rcvr, "receiver")
        self.assertEqual(toa.length, 30)
        self.assertEqual(toa.subint, 2)

    def test_toa_metadata_is_blank_when_project_metadata_is_unavailable(self):
        project = Project.objects.create(
            code="SYNTHETIC-NO-TOA-METADATA",
            short="SYN-TOA-NO",
            main_project=self.main_project,
            toa_metadata_available=False,
        )

        toa = self.create_toa(project)

        self.assertIsNone(toa.nch)
        self.assertIsNone(toa.chan)
        self.assertIsNone(toa.rcvr)
        self.assertIsNone(toa.length)
        self.assertIsNone(toa.subint)
