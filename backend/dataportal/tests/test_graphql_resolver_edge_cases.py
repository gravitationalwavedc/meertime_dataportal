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
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
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

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

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
            query {
                observation(mainProject: "NONEXISTENT") {
                    edges {
                        node {
                            modeDuration
                        }
                    }
                }
            }
        """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content, f"Expected no errors but got: {content.get('errors')}")

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
