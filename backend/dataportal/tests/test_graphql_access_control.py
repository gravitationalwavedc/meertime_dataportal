import json
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from graphene.relay import Node
from graphene_django.utils.testing import GraphQLTestCase

from dataportal.models import (
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    PipelineRun,
    Project,
    ProjectMembership,
    Pulsar,
    PulsarFoldResult,
    Telescope,
    Template,
    Toa,
)
from dataportal.tests.test_base import BaseTestCaseWithTempMedia


class GraphQLAccessControlTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.telescope = Telescope.objects.create(name="TestScope")
        cls.main_project = MainProject.objects.create(name="MeerTIME", telescope=cls.telescope)
        cls.project = Project.objects.create(
            code="SCI-TEST-001",
            short="TEST",
            main_project=cls.main_project,
            embargo_period=timedelta(days=30),
        )
        cls.pulsar = Pulsar.objects.create(name="J0000+0000", comment="Test pulsar")
        cls.calibration = Calibration.objects.create(
            schedule_block_id="cal-001",
            calibration_type="pre",
            location="test",
        )

        now = timezone.now()
        cls.public_time = now - timedelta(days=60)
        cls.embargoed_time = now - timedelta(days=5)

        cls.ephemeris_public = Ephemeris.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            ephemeris_data='{"id":"public"}',
            p0=1.0,
            dm=1.0,
            valid_from=cls.public_time,
            valid_to=cls.public_time + timedelta(days=1),
        )
        Ephemeris.objects.filter(pk=cls.ephemeris_public.pk).update(created_at=cls.public_time)
        cls.ephemeris_public.refresh_from_db()

        cls.ephemeris_embargoed = Ephemeris.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            ephemeris_data='{"id":"embargoed"}',
            p0=2.0,
            dm=2.0,
            valid_from=cls.embargoed_time,
            valid_to=cls.embargoed_time + timedelta(days=1),
        )

        cls.template_public = Template.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            band="LBAND",
            template_hash="public-template",
        )
        Template.objects.filter(pk=cls.template_public.pk).update(created_at=cls.public_time)
        cls.template_public.refresh_from_db()

        cls.template_embargoed = Template.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            band="LBAND",
            template_hash="embargoed-template",
        )

        cls.observation_public_ephem_public = Observation.objects.create(
            pulsar=cls.pulsar,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            ephemeris=cls.ephemeris_public,
            utc_start=cls.public_time,
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

        cls.observation_public_ephem_embargoed = Observation.objects.create(
            pulsar=cls.pulsar,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            ephemeris=cls.ephemeris_embargoed,
            utc_start=cls.public_time,
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
            duration=60.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )

        cls.observation_embargoed = Observation.objects.create(
            pulsar=cls.pulsar,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            ephemeris=cls.ephemeris_embargoed,
            utc_start=cls.embargoed_time,
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
            duration=60.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )

        cls.pipeline_run_public = PipelineRun.objects.create(
            observation=cls.observation_public_ephem_public,
            ephemeris=cls.ephemeris_public,
            template=cls.template_public,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
        )

        cls.pipeline_run_embargoed = PipelineRun.objects.create(
            observation=cls.observation_public_ephem_embargoed,
            ephemeris=cls.ephemeris_embargoed,
            template=cls.template_embargoed,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
        )
        cls.pipeline_run_on_embargoed_observation = PipelineRun.objects.create(
            observation=cls.observation_embargoed,
            ephemeris=cls.ephemeris_embargoed,
            template=cls.template_embargoed,
            pipeline_name="pipe",
            pipeline_version="1.0",
            created_by="test",
            location="local",
        )

        cls.pfr = PulsarFoldResult.objects.create(
            observation=cls.observation_public_ephem_embargoed,
            pipeline_run=cls.pipeline_run_embargoed,
            pulsar=cls.pulsar,
        )

        cls.toa = Toa.objects.create(
            pipeline_run=cls.pipeline_run_public,
            observation=cls.observation_public_ephem_public,
            project=cls.project,
            ephemeris=cls.ephemeris_public,
            template=cls.template_public,
            archive="test.ar",
            freq_MHz=1400.0,
            mjd=Decimal("59000.0"),
            mjd_err=0.1,
            telescope="TEST",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            obs_npol=4,
            day_of_year=1.0,
            binary_orbital_phase=0.1,
            residual_sec=0.0,
            residual_sec_err=0.1,
            residual_phase=0.0,
            residual_phase_err=0.1,
        )
        cls.toa_embargoed = Toa.objects.create(
            pipeline_run=cls.pipeline_run_on_embargoed_observation,
            observation=cls.observation_embargoed,
            project=cls.project,
            ephemeris=cls.ephemeris_embargoed,
            template=cls.template_embargoed,
            archive="embargoed.ar",
            freq_MHz=1400.0,
            mjd=Decimal("59001.0"),
            mjd_err=0.1,
            telescope="TEST",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            obs_npol=4,
            day_of_year=2.0,
            binary_orbital_phase=0.2,
            residual_sec=0.0,
            residual_sec_err=0.1,
            residual_phase=0.0,
            residual_phase_err=0.1,
        )

        cls.member_user = get_user_model().objects.create_user(
            username="member",
            email="member@example.com",
            password="pw",
        )
        cls.outsider_user = get_user_model().objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="pw",
        )
        ProjectMembership.objects.create(
            user=cls.member_user,
            project=cls.project,
            role=ProjectMembership.RoleChoices.MEMBER,
            is_active=True,
        )

    def test_anonymous_filters_embargoed_observations(self):
        response = self.query(
            """
            query {
              observation(first: 10) {
                edges {
                  node {
                    id
                    project { short }
                    ephemeris {
                      id
                      project { short }
                    }
                  }
                }
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        edges = content["data"]["observation"]["edges"]
        obs_nodes = {edge["node"]["id"]: edge["node"] for edge in edges}

        public_public_id = Node.to_global_id("ObservationNode", self.observation_public_ephem_public.id)
        public_embargoed_id = Node.to_global_id("ObservationNode", self.observation_public_ephem_embargoed.id)
        embargoed_id = Node.to_global_id("ObservationNode", self.observation_embargoed.id)

        self.assertIn(public_public_id, obs_nodes)
        self.assertIn(public_embargoed_id, obs_nodes)
        self.assertNotIn(embargoed_id, obs_nodes)

        self.assertEqual(obs_nodes[public_public_id]["project"]["short"], "TEST")
        self.assertEqual(obs_nodes[public_embargoed_id]["project"]["short"], "TEST")
        self.assertIsNotNone(obs_nodes[public_public_id]["ephemeris"])
        self.assertEqual(obs_nodes[public_public_id]["ephemeris"]["project"]["short"], "TEST")
        self.assertIsNone(obs_nodes[public_embargoed_id]["ephemeris"])

    def test_member_can_access_embargoed_data(self):
        self.client.force_login(self.member_user)
        response = self.query(
            """
            query {
              observation(first: 10) {
                edges {
                  node {
                    id
                    ephemeris { id }
                  }
                }
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        edges = content["data"]["observation"]["edges"]
        obs_nodes = {edge["node"]["id"]: edge["node"] for edge in edges}

        embargoed_id = Node.to_global_id("ObservationNode", self.observation_embargoed.id)
        self.assertIn(embargoed_id, obs_nodes)
        self.assertIsNotNone(obs_nodes[embargoed_id]["ephemeris"])

    def test_anonymous_fk_guards(self):
        response = self.query(
            """
            query {
              observation(first: 10) {
                edges {
                  node {
                    id
                    toas(first: 5) {
                      edges {
                        node {
                          id
                          project { id short }
                          ephemeris {
                            id
                            project { short }
                          }
                          template {
                            id
                            project { short }
                          }
                        }
                      }
                    }
                  }
                }
              }
              pulsarFoldResult(first: 5) {
                edges {
                  node {
                    id
                    project { id short }
                    pipelineRun {
                      id
                      template { id }
                    }
                  }
                }
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        for obs_edge in content["data"]["observation"]["edges"]:
            for toa_edge in obs_edge["node"]["toas"]["edges"]:
                self.assertIsNotNone(toa_edge["node"]["project"])
                self.assertEqual(toa_edge["node"]["project"]["short"], "TEST")
                self.assertIsNotNone(toa_edge["node"]["ephemeris"])
                self.assertEqual(toa_edge["node"]["ephemeris"]["project"]["short"], "TEST")
                if toa_edge["node"]["template"] is not None:
                    self.assertEqual(toa_edge["node"]["template"]["project"]["short"], "TEST")

        for pfr_edge in content["data"]["pulsarFoldResult"]["edges"]:
            self.assertIsNotNone(pfr_edge["node"]["project"])
            self.assertEqual(pfr_edge["node"]["project"]["short"], "TEST")
            pipeline_run = pfr_edge["node"]["pipelineRun"]
            self.assertIsNotNone(pipeline_run)
            self.assertIsNone(pipeline_run["template"])

    def test_anonymous_pfr_rows_remain_visible_while_images_and_toas_link_are_redacted(self):
        response = self.query(
            """
            query {
              pulsarFoldResult(pulsar: "J0000+0000", mainProject: "MeerTIME") {
                toasLink
                edges {
                  node {
                    id
                    images {
                      edges {
                        node {
                          id
                        }
                      }
                    }
                  }
                }
              }
            }
            """
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)

        edges = content["data"]["pulsarFoldResult"]["edges"]
        self.assertTrue(edges)
        self.assertIsNone(content["data"]["pulsarFoldResult"]["toasLink"])
        for edge in edges:
            self.assertEqual(edge["node"]["images"]["edges"], [])

    def test_anonymous_node_lookup_can_fetch_embargoed_pfr_with_redacted_images(self):
        pfr_id = Node.to_global_id("PulsarFoldResultNode", self.pfr.id)
        response = self.query(
            """
            query ($id: ID!) {
              node(id: $id) {
                __typename
                ... on PulsarFoldResultNode {
                  id
                  project { short }
                  images {
                    edges {
                      node { id }
                    }
                  }
                }
              }
            }
            """,
            variables={"id": pfr_id},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertIsNotNone(content["data"]["node"])
        self.assertEqual(content["data"]["node"]["project"]["short"], "TEST")
        self.assertEqual(content["data"]["node"]["images"]["edges"], [])

    def test_anonymous_node_lookup_cannot_fetch_embargoed_observation(self):
        embargoed_observation_id = Node.to_global_id("ObservationNode", self.observation_embargoed.id)
        response = self.query(
            """
            query ($id: ID!) {
              node(id: $id) {
                __typename
                ... on ObservationNode {
                  id
                }
              }
            }
            """,
            variables={"id": embargoed_observation_id},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["node"])

    def test_anonymous_node_lookup_cannot_fetch_embargoed_ephemeris(self):
        embargoed_ephemeris_id = Node.to_global_id("EphemerisNode", self.ephemeris_embargoed.id)
        response = self.query(
            """
            query ($id: ID!) {
              node(id: $id) {
                __typename
                ... on EphemerisNode {
                  id
                }
              }
            }
            """,
            variables={"id": embargoed_ephemeris_id},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["node"])

    def test_anonymous_node_lookup_can_fetch_public_ephemeris_project(self):
        public_ephemeris_id = Node.to_global_id("EphemerisNode", self.ephemeris_public.id)
        response = self.query(
            """
            query ($id: ID!) {
              node(id: $id) {
                __typename
                ... on EphemerisNode {
                  id
                  project { short }
                }
              }
            }
            """,
            variables={"id": public_ephemeris_id},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertIsNotNone(content["data"]["node"])
        self.assertEqual(content["data"]["node"]["project"]["short"], "TEST")

    def test_anonymous_node_lookup_cannot_fetch_embargoed_template(self):
        embargoed_template_id = Node.to_global_id("TemplateNode", self.template_embargoed.id)
        response = self.query(
            """
            query ($id: ID!) {
              node(id: $id) {
                __typename
                ... on TemplateNode {
                  id
                }
              }
            }
            """,
            variables={"id": embargoed_template_id},
        )
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        self.assertIsNone(content["data"]["node"])

    def test_non_member_pipeline_run_queryset_excludes_embargoed_observation_runs(self):
        self.client.force_login(self.outsider_user)
        response = self.query(
            """
            query {
              pipelineRun(first: 20) {
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
        self.assertNotIn("errors", content)

        ids = [edge["node"]["id"] for edge in content["data"]["pipelineRun"]["edges"]]
        embargoed_pipeline_run_id = Node.to_global_id(
            "PipelineRunNode",
            self.pipeline_run_on_embargoed_observation.id,
        )
        self.assertNotIn(embargoed_pipeline_run_id, ids)

    def test_non_member_toa_queryset_excludes_embargoed_observation_toas(self):
        self.client.force_login(self.outsider_user)
        response = self.query(
            """
            query {
              toa(first: 20) {
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
        self.assertNotIn("errors", content)

        ids = [edge["node"]["id"] for edge in content["data"]["toa"]["edges"]]
        embargoed_toa_id = Node.to_global_id("ToaNode", self.toa_embargoed.id)
        self.assertNotIn(embargoed_toa_id, ids)

    def test_non_member_pfr_image_guards_query_count_stays_flat_with_more_rows(self):
        self.client.force_login(self.outsider_user)
        query = """
            query {
              pulsarFoldResult(pulsar: "J0000+0000", mainProject: "MeerTIME") {
                edges {
                  node {
                    id
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

        with CaptureQueriesContext(connection) as captured:
            baseline_response = self.query(query)
        baseline_content = json.loads(baseline_response.content)
        self.assertNotIn("errors", baseline_content)
        baseline_queries = len(captured)

        for idx in range(6):
            obs = Observation.objects.create(
                pulsar=self.pulsar,
                telescope=self.telescope,
                project=self.project,
                calibration=self.calibration,
                ephemeris=self.ephemeris_embargoed,
                utc_start=self.embargoed_time - timedelta(hours=idx + 1),
                frequency=1400.0,
                bandwidth=400.0,
                nchan=1024,
                beam=100 + idx,
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
            run = PipelineRun.objects.create(
                observation=obs,
                ephemeris=self.ephemeris_embargoed,
                template=self.template_embargoed,
                pipeline_name="pipe",
                pipeline_version="1.0",
                created_by="test",
                location="local",
            )
            PulsarFoldResult.objects.create(
                observation=obs,
                pipeline_run=run,
                pulsar=self.pulsar,
            )

        with CaptureQueriesContext(connection) as captured:
            expanded_response = self.query(query)
        expanded_content = json.loads(expanded_response.content)
        self.assertNotIn("errors", expanded_content)
        expanded_queries = len(captured)
        self.assertLessEqual(expanded_queries, baseline_queries + 2)

    def test_is_restricted_uses_annotation_without_extra_queries(self):
        observation_items = list(Observation.objects.accessible_to(self.outsider_user))
        ephemeris_items = list(Ephemeris.objects.accessible_to(self.member_user))
        template_items = list(Template.objects.accessible_to(self.member_user))
        toa_items = list(Toa.objects.accessible_to(self.member_user))

        self.assertTrue(observation_items)
        self.assertTrue(ephemeris_items)
        self.assertTrue(template_items)
        self.assertTrue(toa_items)

        with CaptureQueriesContext(connection) as captured:
            self.assertTrue(all(not obs.is_restricted(self.outsider_user) for obs in observation_items))
            self.assertTrue(all(not eph.is_restricted(self.member_user) for eph in ephemeris_items))
            self.assertTrue(all(not tmpl.is_restricted(self.member_user) for tmpl in template_items))
            self.assertTrue(all(not toa.is_restricted(self.member_user) for toa in toa_items))
        self.assertEqual(len(captured), 0)

    def test_is_restricted_fallback_single_lookup_matches_policy(self):
        observation = Observation.objects.get(pk=self.observation_embargoed.pk)
        ephemeris = Ephemeris.objects.get(pk=self.ephemeris_embargoed.pk)
        template = Template.objects.get(pk=self.template_embargoed.pk)
        toa = Toa.objects.get(pk=self.toa_embargoed.pk)

        self.assertFalse(hasattr(observation, "_is_accessible"))
        self.assertFalse(hasattr(ephemeris, "_is_accessible"))
        self.assertFalse(hasattr(template, "_is_accessible"))
        self.assertFalse(hasattr(toa, "_is_accessible"))

        with self.assertNumQueries(1):
            self.assertTrue(observation.is_restricted(self.outsider_user))
        with self.assertNumQueries(1):
            self.assertFalse(observation.is_restricted(self.member_user))

        with self.assertNumQueries(1):
            self.assertTrue(ephemeris.is_restricted(self.outsider_user))
        with self.assertNumQueries(1):
            self.assertFalse(ephemeris.is_restricted(self.member_user))

        with self.assertNumQueries(1):
            self.assertTrue(template.is_restricted(self.outsider_user))
        with self.assertNumQueries(1):
            self.assertFalse(template.is_restricted(self.member_user))

        with self.assertNumQueries(1):
            self.assertTrue(toa.is_restricted(self.outsider_user))
        with self.assertNumQueries(1):
            self.assertFalse(toa.is_restricted(self.member_user))
