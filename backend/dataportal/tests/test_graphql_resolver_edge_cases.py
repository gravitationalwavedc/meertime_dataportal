"""
Regression tests for GraphQL resolver edge cases.

Tests for:
- mainProject without required `name` argument (HIGH 3)
- resolve_mode_duration with empty results (MEDIUM 4)
- Connection resolvers on empty result sets (MEDIUM 5)
- N+1 queries in ephemeris/template resolvers (MEDIUM 6)
- Dead code in filter methods (LOW 9)
- select_related on M2M badges (LOW 10)
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from graphene_django.utils.testing import GraphQLTestCase

from dataportal.models import (
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    PipelineRun,
    Project,
    Pulsar,
    PulsarFoldResult,
    PulsarFoldSummary,
    Telescope,
    Template,
    Toa,
)
from dataportal.tests.test_base import BaseTestCaseWithTempMedia

User = get_user_model()


class ResolverEdgeCaseTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    """Test resolver edge cases: optional args, empty results, missing data."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="password123")
        cls.telescope = Telescope.objects.create(name="TestScope")
        cls.main_project = MainProject.objects.create(name="MeerTIME", telescope=cls.telescope)
        cls.project = Project.objects.create(
            code="SCI-TEST-001",
            short="TEST",
            main_project=cls.main_project,
            embargo_period=timedelta(days=0),
        )
        cls.pulsar = Pulsar.objects.create(name="J0000+0000", comment="Test pulsar")
        cls.calibration = Calibration.objects.create(
            schedule_block_id="cal-001",
            calibration_type="pre",
            location="test",
        )

        now = timezone.now()
        cls.observation = Observation.objects.create(
            pulsar=cls.pulsar,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            utc_start=now - timedelta(days=60),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=1,
            nant=1,
            nant_eff=1,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=60.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )

        cls.ephemeris = Ephemeris.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            created_by=cls.user,
            ephemeris_data="test",
            p0=Decimal("0.001"),
            dm=Decimal("10.0"),
            valid_from=now - timedelta(days=90),
            valid_to=now,
        )

        cls.template = Template.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            band="L-band",
            created_by=cls.user,
        )

        cls.pipeline_run = PipelineRun.objects.create(
            observation=cls.observation,
            ephemeris=cls.ephemeris,
            template=cls.template,
            dm=Decimal("10.0"),
            dm_err=Decimal("0.01"),
            dm_epoch=Decimal("55000.0"),
            dm_chi2r=Decimal("1.0"),
            dm_tres=Decimal("0.001"),
            sn=Decimal("20.0"),
            flux=Decimal("1.0"),
            rm=Decimal("10.0"),
            rm_err=Decimal("0.1"),
            percent_rfi_zapped=0.0,
        )

        cls.fold_result = PulsarFoldResult.objects.create(
            observation=cls.observation,
            pipeline_run=cls.pipeline_run,
            pulsar=cls.pulsar,
        )

        cls.toa = Toa.objects.create(
            pipeline_run=cls.pipeline_run,
            observation=cls.observation,
            project=cls.project,
            ephemeris=cls.ephemeris,
            template=cls.template,
            archive="test.ar",
            freq_MHz=1400.0,
            mjd=Decimal("59000.000000000000"),
            mjd_err=0.001,
            telescope="TestScope",
            dm_corrected=False,
            nsub_type="1",
        )

        cls.telescope_agg = Telescope.objects.create(name="Aggregate Scope")
        cls.main_project_agg = MainProject.objects.create(name="MeerTIME-AGG", telescope=cls.telescope_agg)
        cls.project_alt = Project.objects.create(
            code="SCI-TEST-002",
            short="ALT",
            main_project=cls.main_project_agg,
            embargo_period=timedelta(days=0),
        )
        cls.project_agg_primary = Project.objects.create(
            code="SCI-TEST-003",
            short="TESTAGG",
            main_project=cls.main_project_agg,
            embargo_period=timedelta(days=0),
        )

        cls.pulsar_agg = Pulsar.objects.create(name="J1111+1111", comment="Aggregate test pulsar")
        cls.ephemeris_agg = Ephemeris.objects.create(
            pulsar=cls.pulsar_agg,
            project=cls.project_agg_primary,
            created_by=cls.user,
            ephemeris_data="agg",
            p0=Decimal("0.002"),
            dm=Decimal("11.0"),
            valid_from=now - timedelta(days=30),
            valid_to=now + timedelta(days=30),
        )
        cls.template_agg = Template.objects.create(
            pulsar=cls.pulsar_agg,
            project=cls.project_agg_primary,
            band="L-band",
            created_by=cls.user,
        )

        cls.observation_agg_a = Observation.objects.create(
            pulsar=cls.pulsar_agg,
            telescope=cls.telescope,
            project=cls.project_agg_primary,
            calibration=cls.calibration,
            utc_start=now - timedelta(days=10),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=2,
            nant=1,
            nant_eff=1,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=3600.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )
        cls.observation_agg_b = Observation.objects.create(
            pulsar=cls.pulsar_agg,
            telescope=cls.telescope,
            project=cls.project_alt,
            calibration=cls.calibration,
            utc_start=now - timedelta(days=8),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=3,
            nant=1,
            nant_eff=1,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=7200.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )

        cls.pipeline_run_agg_a = PipelineRun.objects.create(
            observation=cls.observation_agg_a,
            ephemeris=cls.ephemeris_agg,
            template=cls.template_agg,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
            toas_download_link="https://example.com/toas-a",
            sn=Decimal("30.0"),
        )
        cls.pipeline_run_agg_b = PipelineRun.objects.create(
            observation=cls.observation_agg_b,
            ephemeris=cls.ephemeris_agg,
            template=cls.template_agg,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
            toas_download_link="https://example.com/toas-b",
            sn=Decimal("35.0"),
        )

        cls.fold_result_agg_a = PulsarFoldResult.objects.create(
            observation=cls.observation_agg_a,
            pipeline_run=cls.pipeline_run_agg_a,
            pulsar=cls.pulsar_agg,
        )
        cls.fold_result_agg_b = PulsarFoldResult.objects.create(
            observation=cls.observation_agg_b,
            pipeline_run=cls.pipeline_run_agg_b,
            pulsar=cls.pulsar_agg,
        )

        cls.toa_agg_a = Toa.objects.create(
            pipeline_run=cls.pipeline_run_agg_a,
            observation=cls.observation_agg_a,
            project=cls.project,
            ephemeris=cls.ephemeris_agg,
            template=cls.template_agg,
            archive="agg-a.ar",
            freq_MHz=1400.0,
            mjd=Decimal("59010.000000000000"),
            mjd_err=0.001,
            telescope="TestScope",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            snr=12.0,
            day_of_year=10.0,
            binary_orbital_phase=0.2,
            residual_sec=0.05,
            residual_sec_err=0.005,
        )
        cls.toa_agg_b = Toa.objects.create(
            pipeline_run=cls.pipeline_run_agg_b,
            observation=cls.observation_agg_b,
            project=cls.project_alt,
            ephemeris=cls.ephemeris_agg,
            template=cls.template_agg,
            archive="agg-b.ar",
            freq_MHz=1400.0,
            mjd=Decimal("59011.000000000000"),
            mjd_err=0.001,
            telescope="TestScope",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            snr=18.0,
            day_of_year=11.0,
            binary_orbital_phase=0.3,
            residual_sec=0.06,
            residual_sec_err=0.006,
        )
        cls.toa_agg_other_nchan = Toa.objects.create(
            pipeline_run=cls.pipeline_run_agg_a,
            observation=cls.observation_agg_a,
            project=cls.project,
            ephemeris=cls.ephemeris_agg,
            template=cls.template_agg,
            archive="agg-c.ar",
            freq_MHz=1400.0,
            mjd=Decimal("59012.000000000000"),
            mjd_err=0.001,
            telescope="TestScope",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=64,
            snr=20.0,
            day_of_year=12.0,
            binary_orbital_phase=0.4,
            residual_sec=0.07,
            residual_sec_err=0.007,
        )

        PulsarFoldSummary.objects.update_or_create(
            pulsar=cls.pulsar_agg,
            main_project=cls.main_project_agg,
            defaults={
                "first_observation": now - timedelta(days=10),
                "latest_observation": now - timedelta(days=8),
                "latest_observation_beam": 3,
                "timespan": 3,
                "number_of_observations": 2,
                "total_integration_hours": 3.0,
                "last_integration_minutes": 120.0,
                "all_bands": "L-band",
                "last_sn": 35.0,
                "highest_sn": 35.0,
                "lowest_sn": 30.0,
                "avg_sn_pipe": 32.5,
                "max_sn_pipe": 35.0,
                "most_common_project": "TESTAGG",
                "all_projects": "TESTAGG, ALT",
            },
        )

        cls.pulsar_invalid = Pulsar.objects.create(name="J2222+2222", comment="Invalid helper paths")
        cls.ephemeris_invalid = Ephemeris.objects.create(
            pulsar=cls.pulsar_invalid,
            project=cls.project,
            created_by=cls.user,
            ephemeris_data="invalid",
            p0=Decimal("0.003"),
            dm=Decimal("12.0"),
            valid_from=now - timedelta(days=30),
            valid_to=now + timedelta(days=30),
        )
        cls.template_invalid = Template.objects.create(
            pulsar=cls.pulsar_invalid,
            project=cls.project,
            band="L-band",
            created_by=cls.user,
        )
        cls.observation_invalid_no_ephem = Observation.objects.create(
            pulsar=cls.pulsar_invalid,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            utc_start=now - timedelta(days=3),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=4,
            nant=1,
            nant_eff=1,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=100.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )
        cls.observation_invalid_no_template = Observation.objects.create(
            pulsar=cls.pulsar_invalid,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            utc_start=now - timedelta(days=2),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=5,
            nant=1,
            nant_eff=1,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=100.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )
        cls.observation_invalid_no_toa = Observation.objects.create(
            pulsar=cls.pulsar_invalid,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            utc_start=now - timedelta(days=1),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=6,
            nant=1,
            nant_eff=1,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=100.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )
        cls.pipeline_run_invalid_no_ephem = PipelineRun.objects.create(
            observation=cls.observation_invalid_no_ephem,
            ephemeris=None,
            template=cls.template_invalid,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
        )
        cls.pipeline_run_invalid_no_template = PipelineRun.objects.create(
            observation=cls.observation_invalid_no_template,
            ephemeris=cls.ephemeris_invalid,
            template=None,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
        )
        cls.pipeline_run_invalid_no_toa = PipelineRun.objects.create(
            observation=cls.observation_invalid_no_toa,
            ephemeris=cls.ephemeris_invalid,
            template=cls.template_invalid,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
        )
        PulsarFoldResult.objects.create(
            observation=cls.observation_invalid_no_ephem,
            pipeline_run=cls.pipeline_run_invalid_no_ephem,
            pulsar=cls.pulsar_invalid,
        )
        PulsarFoldResult.objects.create(
            observation=cls.observation_invalid_no_template,
            pipeline_run=cls.pipeline_run_invalid_no_template,
            pulsar=cls.pulsar_invalid,
        )
        PulsarFoldResult.objects.create(
            observation=cls.observation_invalid_no_toa,
            pipeline_run=cls.pipeline_run_invalid_no_toa,
            pulsar=cls.pulsar_invalid,
        )

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def _run_query_with_count(self, query, variables=None):
        with CaptureQueriesContext(connection) as captured:
            response = self.query(query, variables=variables)
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")
        return len(captured), content

    def test_pulsar_fold_result_connection_not_truncated_to_100_by_default(self):
        """
        Regression guard for FoldDetail missing rows:
        pulsarFoldResult should return >100 rows when available.
        """
        now = timezone.now()
        for i in range(110):
            observation = Observation.objects.create(
                pulsar=self.pulsar,
                telescope=self.telescope,
                project=self.project,
                calibration=self.calibration,
                utc_start=now - timedelta(days=120 + i),
                frequency=1400.0,
                bandwidth=400.0,
                nchan=1024,
                beam=(i % 63) + 1,
                nant=1,
                nant_eff=1,
                npol=2,
                obs_type="fold",
                raj="00:00:00",
                decj="-00:00:00",
                duration=60.0,
                nbit=8,
                tsamp=0.001,
                fold_nbin=128,
                fold_nchan=128,
                fold_tsubint=10,
            )
            pipeline_run = PipelineRun.objects.create(
                observation=observation,
                ephemeris=self.ephemeris,
                template=self.template,
                pipeline_name="pipe",
                pipeline_version="1.0",
                created_by="test",
                location="local",
                sn=20.0,
            )
            PulsarFoldResult.objects.create(
                observation=observation,
                pipeline_run=pipeline_run,
                pulsar=self.pulsar,
            )

        response = self.query(
            """
            query {
              pulsarFoldResult(pulsar: "J0000+0000", mainProject: "MeerTIME") {
                edges {
                  node { id }
                }
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        edges = content["data"]["pulsarFoldResult"]["edges"]
        unique_ids = {edge["node"]["id"] for edge in edges if edge.get("node")}
        self.assertGreater(len(unique_ids), 100)

    # ── HIGH 3: mainProject without name should not crash ──────────────

    def test_main_project_query_without_name_returns_results(self):
        """mainProject query without name arg should return all projects, not crash."""
        response = self.query(
            """
            query {
                mainProject {
                    edges {
                        node {
                            name
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")
        edges = content["data"]["mainProject"]["edges"]
        self.assertGreaterEqual(len(edges), 1)

    def test_main_project_query_with_name_still_works(self):
        """mainProject query with name arg should still filter correctly."""
        response = self.query(
            """
            query {
                mainProject(name: "MeerTIME") {
                    edges {
                        node {
                            name
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        edges = content["data"]["mainProject"]["edges"]
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["node"]["name"], "MeerTIME")

    # ── MEDIUM 4: resolve_mode_duration empty results ──────────────────

    def test_mode_duration_with_no_matching_observations(self):
        """modeDuration should return None when no observations match, not IndexError."""
        response = self.query(
            """
            query ($targetProject: String!, $mainProject: String!) {
                mainProject(name: $mainProject) {
                    edges {
                        node {
                            name
                        }
                    }
                }
                observation(mainProject: $targetProject) {
                    edges {
                        node {
                            modeDuration
                        }
                    }
                }
            }
        """,
            variables={"targetProject": "MeerTIME", "mainProject": "NONEXISTENT"},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")
        durations = [edge["node"]["modeDuration"] for edge in content["data"]["observation"]["edges"]]
        self.assertTrue(durations)
        self.assertTrue(all(duration is None for duration in durations))

    # ── MEDIUM 5: Connection resolvers on empty result sets ────────────

    def test_most_common_project_empty_connection(self):
        """resolve_most_common_project should handle empty iterable, not AttributeError."""
        response = self.query(
            """
            query {
                pulsarFoldResult(mainProject: "NONEXISTENT") {
                    mostCommonProject
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

    def test_toas_link_empty_connection(self):
        """resolve_toas_link should handle empty iterable, not AttributeError."""
        response = self.query(
            """
            query {
                pulsarFoldResult(mainProject: "NONEXISTENT") {
                    toasLink
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

    def test_description_empty_connection(self):
        """resolve_description should handle empty iterable, not AttributeError."""
        response = self.query(
            """
            query {
                pulsarFoldResult(mainProject: "NONEXISTENT") {
                    description
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

    def test_max_min_plot_length_empty_database(self):
        """resolve_max/min_plot_length should handle no PulsarFoldResults gracefully."""
        response = self.query(
            """
            query {
                pulsarFoldResult(pulsar: "J9999+9999", mainProject: "MeerTIME") {
                    maxPlotLength
                    minPlotLength
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

    # ── MEDIUM 6: N+1 in _get_accessible_ephemeris/template_pfr ────────

    def test_folding_ephemeris_resolver(self):
        """foldingEphemeris resolver should not crash and should use efficient queries."""
        response = self.query(
            """
            query {
                pulsarFoldResult(pulsar: "J0000+0000", mainProject: "MeerTIME") {
                    foldingEphemeris {
                        id
                        dm
                    }
                    foldingEphemerisIsEmbargoed
                    foldingEphemerisExistsButInaccessible
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

    def test_folding_template_resolver(self):
        """foldingTemplate resolver should not crash and should use efficient queries."""
        response = self.query(
            """
            query {
                pulsarFoldResult(pulsar: "J0000+0000", mainProject: "MeerTIME") {
                    foldingTemplate {
                        id
                    }
                    foldingTemplateIsEmbargoed
                    foldingTemplateExistsButInaccessible
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

    def test_folding_helpers_query_count_stays_flat_with_more_rows(self):
        query = """
            query ($pulsar: String!, $mainProject: String!) {
                pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
                    foldingEphemeris { id }
                    foldingEphemerisIsEmbargoed
                    foldingEphemerisExistsButInaccessible
                    foldingTemplate { id }
                    foldingTemplateIsEmbargoed
                    foldingTemplateExistsButInaccessible
                    edges { node { id } }
                }
            }
        """
        variables = {"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG"}
        baseline_queries, _ = self._run_query_with_count(query, variables=variables)

        for idx in range(6):
            obs = Observation.objects.create(
                pulsar=self.pulsar_agg,
                telescope=self.telescope,
                project=self.project_agg_primary,
                calibration=self.calibration,
                utc_start=timezone.now() - timedelta(days=30 + idx),
                frequency=1400.0,
                bandwidth=400.0,
                nchan=1024,
                beam=30 + idx,
                nant=1,
                nant_eff=1,
                npol=2,
                obs_type="fold",
                raj="00:00:00",
                decj="-00:00:00",
                duration=1800.0,
                nbit=8,
                tsamp=0.001,
                fold_nbin=128,
                fold_nchan=128,
                fold_tsubint=10,
            )
            run = PipelineRun.objects.create(
                observation=obs,
                ephemeris=self.ephemeris_agg,
                template=self.template_agg,
                pipeline_name="pipe",
                pipeline_version="1.0",
                created_by="test",
                location="local",
                toas_download_link=f"https://example.com/extra-{idx}",
                sn=Decimal("36.0"),
            )
            PulsarFoldResult.objects.create(
                observation=obs,
                pipeline_run=run,
                pulsar=self.pulsar_agg,
            )
            Toa.objects.create(
                pipeline_run=run,
                observation=obs,
                project=self.project_agg_primary,
                ephemeris=self.ephemeris_agg,
                template=self.template_agg,
                archive=f"agg-extra-{idx}.ar",
                freq_MHz=1400.0,
                mjd=Decimal(f"5903{idx}.0"),
                mjd_err=0.001,
                telescope="TestScope",
                dm_corrected=False,
                nsub_type="1",
                obs_nchan=32,
                snr=14.0,
                day_of_year=20.0 + idx,
                binary_orbital_phase=0.1,
                residual_sec=0.02,
                residual_sec_err=0.002,
            )

        expanded_queries, _ = self._run_query_with_count(query, variables=variables)
        self.assertLessEqual(expanded_queries, baseline_queries + 2)

    def test_toa_fk_guard_query_count_stays_flat_with_more_rows(self):
        query = """
            query ($pulsar: String!, $mainProject: String!) {
                toa(pulsar: $pulsar, mainProject: $mainProject) {
                    edges {
                        node {
                            id
                            project { id }
                            ephemeris { id }
                            template { id }
                            pipelineRun { id }
                            observation { id }
                        }
                    }
                }
            }
        """
        variables = {"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG"}
        baseline_queries, _ = self._run_query_with_count(query, variables=variables)

        for idx in range(6):
            Toa.objects.create(
                pipeline_run=self.pipeline_run_agg_a,
                observation=self.observation_agg_a,
                project=self.project_agg_primary,
                ephemeris=self.ephemeris_agg,
                template=self.template_agg,
                archive=f"toa-fk-extra-{idx}.ar",
                freq_MHz=1400.0,
                mjd=Decimal(f"5914{idx}.0"),
                mjd_err=0.001,
                telescope="TestScope",
                dm_corrected=False,
                nsub_type="1",
                obs_nchan=32,
                snr=22.0,
                day_of_year=25.0 + idx,
                binary_orbital_phase=0.5,
                residual_sec=0.04,
                residual_sec_err=0.004,
            )

        expanded_queries, _ = self._run_query_with_count(query, variables=variables)
        self.assertLessEqual(expanded_queries, baseline_queries + 2)

    def test_fold_detail_query_count_budget(self):
        query = """
            query ($pulsar: String!, $mainProject: String!) {
                pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
                    toasLink
                    allProjects
                    allNchans
                    edges {
                        node {
                            id
                            observation {
                                id
                                utcStart
                                project { short }
                                ephemeris { dm }
                                calibration { idInt }
                            }
                            pipelineRun {
                                id
                                dm
                                createdAt
                                observation {
                                    calibration {
                                        badges {
                                            edges {
                                                node { name }
                                            }
                                        }
                                    }
                                }
                            }
                            images {
                                edges {
                                    node { id }
                                }
                            }
                        }
                    }
                }
            }
        """
        query_count, _ = self._run_query_with_count(
            query,
            variables={"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG"},
        )
        self.assertLessEqual(query_count, 80)

    def test_toa_query_count_budget(self):
        query = """
            query ($pulsar: String!, $mainProject: String!) {
                toa(pulsar: $pulsar, mainProject: $mainProject) {
                    edges {
                        node {
                            id
                            project { id short }
                            ephemeris { id dm }
                            template { id }
                            observation { id utcStart }
                            pipelineRun {
                                id
                                observation { id }
                            }
                        }
                    }
                    totalBadgeExcludedToas
                }
            }
        """
        query_count, _ = self._run_query_with_count(
            query,
            variables={"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG"},
        )
        self.assertLessEqual(query_count, 80)

    def test_total_toa_counts_with_and_without_project_filter(self):
        response = self.query(
            """
            query ($pulsar: String!, $mainProject: String!, $projectShort: String!) {
                pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
                    totalAll: totalToa(
                        pulsar: $pulsar,
                        mainProject: $mainProject,
                        nsubType: "1",
                    )
                    totalFiltered: totalToa(
                        pulsar: $pulsar,
                        mainProject: $mainProject,
                        projectShort: $projectShort,
                        nsubType: "1",
                    )
                }
            }
        """,
            variables={"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG", "projectShort": "ALT"},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertEqual(content["data"]["pulsarFoldResult"]["totalAll"], 2)
        self.assertEqual(content["data"]["pulsarFoldResult"]["totalFiltered"], 1)

    def test_custom_aggregate_fields_return_expected_values(self):
        response = self.query(
            """
            query ($pulsar: String!, $mainProject: String!) {
                pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
                    totalObservations
                    totalObservationHours
                    totalProjects
                    totalTimespanDays
                    totalEstimatedDiskSpace
                    edges {
                        node {
                            observation {
                                duration
                                utcStart
                                project {
                                    short
                                }
                            }
                        }
                    }
                }
            }
        """,
            variables={"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG"},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        data = content["data"]["pulsarFoldResult"]
        observations = [edge["node"]["observation"] for edge in data["edges"]]
        self.assertEqual(data["totalObservations"], len(observations))
        expected_hours = int(sum(float(obs["duration"]) for obs in observations) / 3600)
        self.assertEqual(data["totalObservationHours"], expected_hours)
        self.assertEqual(data["totalProjects"], len({obs["project"]["short"] for obs in observations}))
        utc_values = [datetime.fromisoformat(obs["utcStart"].replace("Z", "+00:00")) for obs in observations]
        expected_days = (max(utc_values) - min(utc_values)).days + 1 if utc_values else 0
        self.assertEqual(data["totalTimespanDays"], expected_days)
        self.assertIsInstance(data["totalEstimatedDiskSpace"], str)
        self.assertTrue(data["totalEstimatedDiskSpace"])

    def test_timing_residual_plot_data_honours_project_short_and_formats_output(self):
        response = self.query(
            """
            query ($pulsar: String!, $mainProject: String!, $projectShort: String!) {
                pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
                    timingResidualPlotData(
                        pulsar: $pulsar,
                        mainProject: $mainProject,
                        projectShort: $projectShort,
                        dmCorrected: false,
                        nsubType: "1",
                        obsNchan: 32,
                        minimumSNR: 8,
                    ) {
                        day
                        snr
                        utc
                        link
                    }
                }
            }
        """,
            variables={"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG", "projectShort": "ALT"},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        plot = content["data"]["pulsarFoldResult"]["timingResidualPlotData"]
        self.assertEqual(len(plot), 1)
        self.assertEqual(plot[0]["day"], 11.0)
        self.assertEqual(plot[0]["snr"], 18.0)
        self.assertIsInstance(plot[0]["utc"], float)
        self.assertIn("/MeerTIME-AGG/J1111+1111/", plot[0]["link"])

    def test_custom_connection_fields_with_real_data_and_empty_case(self):
        populated = self.query(
            """
            query ($pulsar: String!, $mainProject: String!) {
                pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
                    allProjects
                    allNchans
                    toasLink
                    mostCommonProject
                }
            }
        """,
            variables={"pulsar": "J1111+1111", "mainProject": "MeerTIME-AGG"},
        )
        populated_content = json.loads(populated.content)
        self.assertNotIn("errors", populated_content)
        populated_data = populated_content["data"]["pulsarFoldResult"]
        self.assertIn("ALT", populated_data["allProjects"])
        self.assertIn(32, populated_data["allNchans"])
        self.assertIn(64, populated_data["allNchans"])
        self.assertIsNotNone(populated_data["toasLink"])
        self.assertIsNotNone(populated_data["mostCommonProject"])

        empty = self.query(
            """
            query {
                pulsarFoldResult(mainProject: "NONEXISTENT") {
                    allProjects
                    allNchans
                    toasLink
                    mostCommonProject
                }
            }
        """
        )
        empty_content = json.loads(empty.content)
        self.assertNotIn("errors", empty_content)
        empty_data = empty_content["data"]["pulsarFoldResult"]
        self.assertEqual(empty_data["allProjects"], [])
        self.assertEqual(empty_data["allNchans"], [])
        self.assertIsNone(empty_data["toasLink"])
        self.assertIsNone(empty_data["mostCommonProject"])

    def test_accessible_helpers_report_no_valid_ephemeris_or_template_when_all_candidates_invalid(self):
        response = self.query(
            """
            query ($pulsar: String!, $mainProject: String!) {
                pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
                    foldingEphemeris {
                        id
                    }
                    foldingEphemerisIsEmbargoed
                    foldingEphemerisExistsButInaccessible
                    foldingTemplate {
                        id
                    }
                    foldingTemplateIsEmbargoed
                    foldingTemplateExistsButInaccessible
                }
            }
        """,
            variables={"pulsar": "J2222+2222", "mainProject": "MeerTIME"},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        data = content["data"]["pulsarFoldResult"]
        self.assertIsNone(data["foldingEphemeris"])
        self.assertIsNone(data["foldingEphemerisIsEmbargoed"])
        self.assertFalse(data["foldingEphemerisExistsButInaccessible"])
        self.assertIsNone(data["foldingTemplate"])
        self.assertIsNone(data["foldingTemplateIsEmbargoed"])
        self.assertFalse(data["foldingTemplateExistsButInaccessible"])

    # ── LOW 9: Dead code in filter methods ─────────────────────────────

    def test_observation_filter_empty_main_project_returns_all(self):
        """Empty string mainProject filter should return all observations (not filter)."""
        response = self.query(
            """
            query {
                observation(mainProject: "") {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")
        edges = content["data"]["observation"]["edges"]
        self.assertGreaterEqual(len(edges), 1)

    def test_observation_filter_empty_project_short_returns_all(self):
        """Empty string project_Short filter should return all observations (not filter)."""
        response = self.query(
            """
            query {
                observation(project_Short: "") {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")
        edges = content["data"]["observation"]["edges"]
        self.assertGreaterEqual(len(edges), 1)

    # ── LOW 10: select_related on M2M badges ───────────────────────────

    def test_timing_residual_plot_data_with_toa(self):
        """timing_residual_plot_data with Toas should not crash from select_related on M2M badges."""
        response = self.query(
            """
            query {
                pulsarFoldResult(pulsar: "J0000+0000", mainProject: "MeerTIME") {
                    timingResidualPlotData(
                        pulsar: "J0000+0000",
                        mainProject: "MeerTIME",
                        dmCorrected: false,
                        nsubType: "1",
                        obsNchan: 0,
                    ) {
                        day
                        snr
                    }
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

    def test_total_badge_excluded_toas_with_toa(self):
        """resolve_total_badge_excluded_toas should not crash from select_related on M2M badges."""
        response = self.query(
            """
            query {
                toa(pulsar: "J0000+0000", mainProject: "MeerTIME") {
                    totalBadgeExcludedToas
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")
