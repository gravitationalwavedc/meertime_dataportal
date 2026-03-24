import json
from decimal import Decimal

from graphene_django.utils.testing import GraphQLTestCase

from dataportal.models import Project, Toa
from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import setup_query_test


class GraphQLFilterSemanticsTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    """Contract tests for standard GraphQL filter behavior (no sentinel values)."""

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
        self._ensure_multiproject_toa_fixture()

    def _ensure_multiproject_toa_fixture(self):
        """Ensure at least one J0125-2327 TOA exists in TPA so projectShort filtering is meaningful."""
        existing = Toa.objects.filter(observation__pulsar__name="J0125-2327", project__short="TPA").exists()
        if existing:
            return

        source_toa = Toa.objects.filter(observation__pulsar__name="J0125-2327").first()
        tpa_project = Project.objects.get(short="TPA")
        Toa.objects.create(
            pipeline_run=source_toa.pipeline_run,
            observation=source_toa.observation,
            project=tpa_project,
            ephemeris=source_toa.ephemeris,
            template=source_toa.template,
            archive=source_toa.archive,
            freq_MHz=source_toa.freq_MHz,
            mjd=source_toa.mjd + Decimal("0.123456"),
            mjd_err=source_toa.mjd_err,
            telescope=source_toa.telescope,
            fe=source_toa.fe,
            be=source_toa.be,
            f=source_toa.f,
            bw=source_toa.bw,
            tobs=source_toa.tobs,
            tmplt=source_toa.tmplt,
            gof=source_toa.gof,
            nbin=source_toa.nbin,
            nch=source_toa.nch,
            chan=source_toa.chan,
            rcvr=source_toa.rcvr,
            snr=source_toa.snr,
            length=source_toa.length,
            subint=source_toa.subint,
            dm_corrected=source_toa.dm_corrected,
            nsub_type=source_toa.nsub_type,
            obs_nchan=source_toa.obs_nchan,
            obs_npol=source_toa.obs_npol,
            day_of_year=source_toa.day_of_year,
            binary_orbital_phase=source_toa.binary_orbital_phase,
            residual_sec=source_toa.residual_sec,
            residual_sec_err=source_toa.residual_sec_err,
            residual_phase=source_toa.residual_phase,
            residual_phase_err=source_toa.residual_phase_err,
        )

    def test_observation_explicit_main_project_matches_unfiltered_for_known_pulsar(self):
        query = """
        query ($pulsars: [String]) {
          withMainProject: observation(pulsar_Name: $pulsars, mainProject: "MeerTIME", first: 100) {
            edges {
              node {
                id
              }
            }
          }
          withoutMainProject: observation(pulsar_Name: $pulsars, first: 100) {
            edges {
              node {
                id
              }
            }
          }
        }
        """
        response = self.query(query, variables={"pulsars": ["J0125-2327"]})
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        with_main_project = {edge["node"]["id"] for edge in content["data"]["withMainProject"]["edges"]}
        without = {edge["node"]["id"] for edge in content["data"]["withoutMainProject"]["edges"]}
        self.assertGreater(len(with_main_project), 0)
        self.assertEqual(with_main_project, without)

    def test_toa_project_short_filters_exact_project(self):
        query = """
        query {
          ptaOnly: toa(
            pulsar: "J0125-2327"
            mainProject: "MeerTIME"
            projectShort: "PTA"
            nsubType: "1"
            obsNchan: 1
            first: 100
          ) {
            edges {
              node {
                id
              }
            }
          }
          withoutProjectShort: toa(
            pulsar: "J0125-2327"
            mainProject: "MeerTIME"
            nsubType: "1"
            obsNchan: 1
            first: 100
          ) {
            edges {
              node {
                id
              }
            }
          }
        }
        """
        response = self.query(query)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        pta_only = {edge["node"]["id"] for edge in content["data"]["ptaOnly"]["edges"]}
        without = {edge["node"]["id"] for edge in content["data"]["withoutProjectShort"]["edges"]}
        self.assertGreater(len(pta_only), 0)
        self.assertGreater(len(without), len(pta_only))
        self.assertTrue(pta_only.issubset(without))

    def test_observation_summary_specific_project_is_subset_of_unfiltered_project(self):
        query = """
        query {
          unfilteredProject: observationSummary(
            pulsar_Name: "J0125-2327"
            obsType: "fold"
            mainProject: "MeerTIME"
            band: "LBAND"
            first: 100
          ) {
            edges {
              node {
                observations
              }
            }
          }
          ptaProject: observationSummary(
            pulsar_Name: "J0125-2327"
            obsType: "fold"
            mainProject: "MeerTIME"
            project_Short: "PTA"
            band: "LBAND"
            first: 100
          ) {
            edges {
              node {
                observations
              }
            }
          }
        }
        """
        response = self.query(query)
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        unfiltered_total = sum(edge["node"]["observations"] for edge in content["data"]["unfilteredProject"]["edges"])
        pta_total = sum(edge["node"]["observations"] for edge in content["data"]["ptaProject"]["edges"])

        self.assertGreater(unfiltered_total, 0)
        self.assertGreaterEqual(unfiltered_total, pta_total)
