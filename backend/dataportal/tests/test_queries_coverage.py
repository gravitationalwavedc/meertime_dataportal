import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from dataportal.graphql import queries
from dataportal.models import (
    Badge,
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    PipelineImage,
    PipelineRun,
    Project,
    ProjectMembership,
    Pulsar,
    PulsarFoldResult,
    Telescope,
    Template,
    Toa,
)
from user_manage.models import User
from utils.constants import UserRole


def make_info(user, variable_values=None):
    return SimpleNamespace(context=SimpleNamespace(user=user), variable_values=variable_values or {})


class QueriesCoverageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = timezone.now()
        cls.user = User.objects.create_user(username="member", email="member@test.com", password="testpass123")
        cls.unrestricted_user = User.objects.create_user(
            username="unrestricted",
            email="unrestricted@test.com",
            password="testpass123",
            role=UserRole.UNRESTRICTED.value,
        )
        cls.superuser = User.objects.create_superuser("admin", "admin@test.com", "testpass123")

        cls.telescope = Telescope.objects.create(name="Scope")
        cls.telescope2 = Telescope.objects.create(name="Scope2")
        cls.main_project = MainProject.objects.create(name="MeerTIME", telescope=cls.telescope)
        cls.private_project = Project.objects.create(
            code="SCI-PRIV-001",
            short="PRIV",
            main_project=cls.main_project,
            embargo_period=timedelta(days=365),
        )
        cls.public_project = Project.objects.create(
            code="SCI-PUB-001",
            short="PUB",
            main_project=cls.main_project,
            embargo_period=timedelta(days=0),
        )
        cls.pulsar = Pulsar.objects.create(name="J0000+0000", comment="pulsar comment")
        cls.calibration = Calibration.objects.create(schedule_block_id="cal-01", calibration_type="pre")

        cls.private_ephemeris = Ephemeris.objects.create(
            pulsar=cls.pulsar,
            project=cls.private_project,
            created_by=cls.user,
            ephemeris_data=json.dumps({"DM": 10.0, "P0": 1.0}),
            p0=1.0,
            dm=10.0,
            valid_from=cls.now - timedelta(days=10),
            valid_to=cls.now + timedelta(days=10),
        )
        cls.private_template = Template.objects.create(
            pulsar=cls.pulsar,
            project=cls.private_project,
            band="LBAND",
            created_by=cls.user,
            template_hash="tmpl-private",
        )

        cls.private_observation = Observation.objects.create(
            pulsar=cls.pulsar,
            telescope=cls.telescope,
            project=cls.private_project,
            calibration=cls.calibration,
            ephemeris=cls.private_ephemeris,
            utc_start=cls.now - timedelta(hours=1),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=1,
            nant=10,
            nant_eff=8,
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
        cls.public_observation = Observation.objects.create(
            pulsar=cls.pulsar,
            telescope=cls.telescope2,
            project=cls.public_project,
            calibration=cls.calibration,
            ephemeris=cls.private_ephemeris,
            utc_start=cls.now - timedelta(days=10),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=2,
            nant=40,
            nant_eff=38,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=200.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )

        cls.private_pipeline_run = PipelineRun.objects.create(
            observation=cls.private_observation,
            ephemeris=cls.private_ephemeris,
            template=cls.private_template,
            pipeline_name="meerpipe",
            pipeline_version="1.0.0",
            created_by="tester",
            location="/tmp",
            job_state="Failed",
            sn=25.0,
            dm=12.0,
            dm_err=0.2,
            percent_rfi_zapped=0.0,
        )
        cls.public_pipeline_run = PipelineRun.objects.create(
            observation=cls.public_observation,
            ephemeris=None,
            template=None,
            pipeline_name="meerpipe",
            pipeline_version="1.0.0",
            created_by="tester",
            location="/tmp",
            job_state="Completed",
            sn=12.0,
            dm=13.0,
            dm_err=0.1,
            percent_rfi_zapped=0.0,
        )

        cls.private_fold_result = PulsarFoldResult.objects.create(
            observation=cls.private_observation,
            pipeline_run=cls.private_pipeline_run,
            pulsar=cls.pulsar,
        )
        cls.public_fold_result = PulsarFoldResult.objects.create(
            observation=cls.public_observation,
            pipeline_run=cls.public_pipeline_run,
            pulsar=cls.pulsar,
        )

        cls.pipeline_image = PipelineImage.objects.create(
            pulsar_fold_result=cls.private_fold_result,
            url="https://example.com/image.png",
            cleaned=True,
            image_type="phase-freq",
            resolution="high",
        )
        cls.badge, _ = Badge.objects.get_or_create(name="DM Drift")
        cls.private_pipeline_run.badges.add(cls.badge)

        cls.toa_private = Toa.objects.create(
            pipeline_run=cls.private_pipeline_run,
            observation=cls.private_observation,
            project=cls.private_project,
            ephemeris=cls.private_ephemeris,
            template=cls.private_template,
            archive="private.ar",
            freq_MHz=1400.0,
            mjd=59000.0,
            mjd_err=0.001,
            telescope="Scope",
            dm_corrected=True,
            nsub_type="1",
            obs_nchan=16,
            obs_npol=2,
            chan=1,
            subint=1,
            snr=5.0,
        )
        cls.toa_public = Toa.objects.create(
            pipeline_run=cls.public_pipeline_run,
            observation=cls.public_observation,
            project=cls.public_project,
            ephemeris=cls.private_ephemeris,
            template=cls.private_template,
            archive="public.ar",
            freq_MHz=1400.0,
            mjd=59001.0,
            mjd_err=0.001,
            telescope="Scope2",
            dm_corrected=False,
            nsub_type="max",
            obs_nchan=1,
            obs_npol=2,
            chan=2,
            subint=2,
            snr=20.0,
        )

        ProjectMembership.objects.create(user=cls.unrestricted_user, project=cls.private_project, is_active=True)

    def test_simple_resolvers_and_filter_methods(self):
        anon_info = make_info(AnonymousUser())
        auth_info = make_info(self.unrestricted_user)

        self.assertEqual(queries.ProjectNode.resolve_embargoPeriod(self.private_project, auth_info), 365)
        self.assertEqual(
            queries.EphemerisNode.resolve_id_int(self.private_ephemeris, auth_info), self.private_ephemeris.id
        )
        self.assertEqual(
            queries.EphemerisNode.resolve_project(self.private_ephemeris, anon_info), self.private_project
        )
        self.assertEqual(
            queries.EphemerisNode.resolve_project(self.private_ephemeris, auth_info), self.private_project
        )
        self.assertEqual(queries.TemplateNode.resolve_project(self.private_template, anon_info), self.private_project)
        self.assertEqual(queries.TemplateNode.resolve_project(self.private_template, auth_info), self.private_project)
        self.assertEqual(queries.CalibrationNode.resolve_id_int(self.calibration, auth_info), self.calibration.id)

        obs_qs = Observation.objects.all()
        obs_filter = queries.ObservationFilterSet()
        self.assertEqual(obs_filter.filter_main_project(obs_qs, "main_project", "").count(), obs_qs.count())
        self.assertEqual(obs_filter.filter_project_short(obs_qs, "project_short", "").count(), obs_qs.count())
        self.assertEqual(
            obs_filter.filter_project_short(obs_qs, "project_short", self.private_project.short).count(),
            obs_qs.filter(project__short=self.private_project.short).count(),
        )
        self.assertEqual(obs_filter.filter_obs_type(obs_qs, "obs_type", "").count(), obs_qs.count())
        self.assertEqual(obs_filter.filter_unprocessed(obs_qs, "unprocessed", False).count(), obs_qs.count())
        self.assertTrue(obs_filter.filter_unprocessed(obs_qs, "unprocessed", True).count() >= 0)
        self.assertEqual(obs_filter.filter_incomplete(obs_qs, "incomplete", False).count(), obs_qs.count())
        self.assertTrue(obs_filter.filter_incomplete(obs_qs, "incomplete", True).count() >= 0)

        pfr_filter = queries.PulsarFoldResultFilterSet()
        self.assertEqual(
            pfr_filter.filter_utc_start(PulsarFoldResult.objects.all(), "utc_start", "").count(),
            PulsarFoldResult.objects.count(),
        )
        self.assertEqual(
            pfr_filter.filter_exclude_badges(PulsarFoldResult.objects.all(), "exclude_badges", []).count(),
            PulsarFoldResult.objects.count(),
        )
        filtered_count = pfr_filter.filter_exclude_badges(
            PulsarFoldResult.objects.all(), "exclude_badges", ["DM Drift"]
        ).count()
        self.assertLessEqual(filtered_count, PulsarFoldResult.objects.count())

        toa_filter = queries.ToaFilterSet()
        self.assertEqual(
            toa_filter.filter_exclude_badges(Toa.objects.all(), "exclude_badges", []).count(),
            Toa.objects.count(),
        )

    def test_connection_aggregate_and_empty_branches(self):
        connection = SimpleNamespace(
            edges=[SimpleNamespace(node=self.private_observation)], iterable=[self.private_observation]
        )
        self.assertEqual(queries.ObservationConnection.resolve_total_observations(connection, None), 1)
        self.assertGreater(queries.ObservationConnection.resolve_total_observation_hours(connection, None), 0)
        self.assertEqual(queries.ObservationConnection.resolve_total_pulsars(connection, None), 1)
        self.assertEqual(queries.ObservationConnection.resolve_total_observations_tel_lt_35(connection, None), 1)

        pfr_conn = SimpleNamespace(
            iterable=[],
            edges=[],
        )
        self.assertEqual(queries.PulsarFoldResultConnection.resolve_total_timespan_days(pfr_conn, None), 0)

        fold_conn_empty = SimpleNamespace(edges=[])
        instance = SimpleNamespace(context=SimpleNamespace(user=self.unrestricted_user))
        self.assertEqual(queries.PulsarFoldSummaryConnection.resolve_total_project_time(fold_conn_empty, instance), 0)
        self.assertEqual(
            queries.PulsarSearchSummaryConnection.resolve_total_project_time(fold_conn_empty, instance), 0
        )

        fold_conn = SimpleNamespace(
            edges=[
                SimpleNamespace(
                    node=SimpleNamespace(
                        number_of_observations=2, total_integration_hours=1.2, most_common_project="PRIV"
                    )
                )
            ]
        )
        search_conn = SimpleNamespace(
            edges=[
                SimpleNamespace(
                    node=SimpleNamespace(
                        number_of_observations=3, total_integration_hours=2.2, most_common_project="PRIV"
                    )
                )
            ]
        )
        self.assertEqual(queries.PulsarFoldSummaryConnection.resolve_total_observations(fold_conn, instance), 2)
        self.assertEqual(queries.PulsarFoldSummaryConnection.resolve_total_pulsars(fold_conn, instance), 1)
        self.assertEqual(queries.PulsarFoldSummaryConnection.resolve_total_observation_time(fold_conn, instance), 1.2)
        self.assertEqual(queries.PulsarSearchSummaryConnection.resolve_total_observations(search_conn, instance), 3)
        self.assertEqual(queries.PulsarSearchSummaryConnection.resolve_total_pulsars(search_conn, instance), 1)
        self.assertEqual(
            queries.PulsarSearchSummaryConnection.resolve_total_observation_time(search_conn, instance), 2.2
        )
        self.assertGreaterEqual(
            queries.PulsarSearchSummaryConnection.resolve_total_project_time(search_conn, instance), 0
        )

        pfr_space_conn = SimpleNamespace(
            iterable=[
                SimpleNamespace(
                    observation=SimpleNamespace(duration=10, fold_tsubint=0, fold_nbin=1, fold_nchan=1, npol=1)
                )
            ]
        )
        self.assertTrue(queries.PulsarFoldResultConnection.resolve_total_estimated_disk_space(pfr_space_conn, None))

    def test_node_guard_resolvers(self):
        info_member = make_info(self.user)
        info_unrestricted = make_info(self.unrestricted_user)
        info_anon = make_info(AnonymousUser())

        public_obs = self.public_observation
        private_obs = self.private_observation

        obs_none_ephem = Observation.objects.create(
            pulsar=self.pulsar,
            telescope=self.telescope,
            project=self.public_project,
            calibration=self.calibration,
            ephemeris=None,
            utc_start=self.now - timedelta(days=30),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=9,
            nant=40,
            nant_eff=38,
            npol=2,
            obs_type="search",
            raj="00:00:00",
            decj="-00:00:00",
            duration=50.0,
            nbit=8,
            tsamp=0.001,
        )
        self.assertIsNone(queries.ObservationNode.resolve_ephemeris(obs_none_ephem, info_member))
        self.assertIsNone(queries.ObservationNode.resolve_ephemeris(public_obs, info_member))
        self.assertEqual(queries.ObservationNode.resolve_project(private_obs, info_anon), self.private_project)
        self.assertIsNone(queries.ObservationNode.resolve_telescope(private_obs, info_anon))

        self.assertEqual(
            queries.PipelineRunNode.resolve_observation(self.private_pipeline_run, info_member),
            self.private_observation,
        )
        self.assertEqual(
            queries.PipelineRunNode.resolve_observation(self.private_pipeline_run, info_unrestricted),
            self.private_observation,
        )
        self.assertIsNone(queries.PipelineRunNode.resolve_ephemeris(self.public_pipeline_run, info_member))
        self.assertIsNone(queries.PipelineRunNode.resolve_ephemeris(self.private_pipeline_run, info_member))
        self.assertEqual(
            queries.PipelineRunNode.resolve_ephemeris(self.private_pipeline_run, info_unrestricted),
            self.private_ephemeris,
        )
        self.assertIsNone(queries.PipelineRunNode.resolve_template(self.public_pipeline_run, info_member))
        self.assertIsNone(queries.PipelineRunNode.resolve_template(self.private_pipeline_run, info_member))
        self.assertEqual(
            queries.PipelineRunNode.resolve_template(self.private_pipeline_run, info_unrestricted),
            self.private_template,
        )
        self.assertEqual(
            queries.PipelineRunNode.resolve_dm_err(self.private_pipeline_run, info_member),
            self.private_pipeline_run.dm_err,
        )

        self.assertEqual(
            queries.PulsarFoldResultNode.resolve_images(self.private_fold_result, info_unrestricted).count(), 1
        )
        self.assertEqual(queries.PulsarFoldResultNode.resolve_images(self.private_fold_result, info_member).count(), 0)
        self.assertEqual(
            queries.PulsarFoldResultNode.resolve_observation(self.private_fold_result, info_member),
            self.private_observation,
        )
        self.assertIsNone(
            queries.PulsarFoldResultNode.resolve_pipeline_run(SimpleNamespace(pipeline_run=None), info_member)
        )
        self.assertEqual(
            queries.PulsarFoldResultNode.resolve_pipeline_run(self.private_fold_result, info_member),
            self.private_pipeline_run,
        )
        self.assertEqual(
            queries.PulsarFoldResultNode.resolve_project(self.private_fold_result, info_anon), self.private_project
        )
        self.assertEqual(
            queries.PulsarFoldResultNode.resolve_project(self.private_fold_result, info_member),
            self.private_project,
        )
        self.assertEqual(
            queries.PulsarFoldResultNode.resolve_project(self.private_fold_result, info_unrestricted),
            self.private_project,
        )
        self.assertIsNone(queries.PulsarFoldResultNode.resolve_next_observation(self.private_fold_result, info_member))
        self.assertIsNotNone(
            queries.PulsarFoldResultNode.resolve_previous_observation(self.private_fold_result, info_member)
        )

        self.assertIsNone(queries.PipelineImageNode.resolve_pulsar_fold_result(self.pipeline_image, info_member))
        self.assertEqual(
            queries.PipelineImageNode.resolve_pulsar_fold_result(self.pipeline_image, info_unrestricted),
            self.private_fold_result,
        )

        self.assertIsNone(queries.ToaNode.resolve_pipeline_run(SimpleNamespace(pipeline_run=None), info_member))
        self.assertIsNone(queries.ToaNode.resolve_pipeline_run(self.toa_private, info_member))
        self.assertIsNone(queries.ToaNode.resolve_observation(self.toa_private, info_member))
        self.assertIsNone(queries.ToaNode.resolve_project(self.toa_private, info_anon))
        self.assertIsNone(queries.ToaNode.resolve_project(self.toa_private, info_member))
        self.assertIsNone(queries.ToaNode.resolve_ephemeris(SimpleNamespace(ephemeris=None), info_member))
        self.assertIsNone(queries.ToaNode.resolve_ephemeris(self.toa_private, info_member))
        self.assertEqual(
            queries.ToaNode.resolve_ephemeris(self.toa_private, info_unrestricted), self.private_ephemeris
        )
        self.assertIsNone(queries.ToaNode.resolve_template(SimpleNamespace(template=None), info_member))
        self.assertIsNone(queries.ToaNode.resolve_template(self.toa_private, info_member))

    def test_toa_connection_filter_branches(self):
        instance = SimpleNamespace(
            context=SimpleNamespace(user=self.unrestricted_user),
            variable_values={"pulsar": self.pulsar.name, "mainProject": "MeerTIME"},
        )
        self.assertIn("PRIV", queries.ToaConnection.resolve_all_projects(SimpleNamespace(), instance))
        self.assertIn(1, queries.ToaConnection.resolve_all_nchans(SimpleNamespace(), instance))

        instance_badges = SimpleNamespace(
            context=SimpleNamespace(user=self.unrestricted_user),
            variable_values={
                "excludeBadges": ["DM Drift"],
                "minimumSNR": 10.0,
                "pipelineRunId": self.private_pipeline_run.id,
                "pulsar": self.pulsar.name,
                "mainProject": "MeerTIME",
                "projectShort": "PRIV",
                "dmCorrected": True,
                "nsubType": "1",
                "obsNchan": 16,
                "obsNpol": 2,
            },
        )
        total = queries.ToaConnection.resolve_total_badge_excluded_toas(SimpleNamespace(), instance_badges)
        self.assertGreaterEqual(total, 1)

    def test_query_resolvers_and_file_paths(self):
        query = queries.Query()
        info_unrestricted = make_info(self.unrestricted_user)

        self.assertEqual(query.resolve_telescope(info_unrestricted).count(), 2)
        self.assertEqual(query.resolve_telescope(info_unrestricted, name="Scope").count(), 1)
        self.assertEqual(query.resolve_main_project(info_unrestricted).count(), 1)
        self.assertEqual(query.resolve_project(info_unrestricted).count(), 2)
        self.assertTrue(query.resolve_ephemeris(info_unrestricted).exists())
        self.assertTrue(query.resolve_template(info_unrestricted).exists())
        self.assertEqual(query.resolve_pipeline_image(info_unrestricted).count(), 1)
        self.assertGreaterEqual(query.resolve_badge(info_unrestricted).count(), 1)
        self.assertEqual(query.resolve_pipeline_run(info_unrestricted).count(), 2)
        self.assertEqual(str(query.resolve_pipeline_run(info_unrestricted, id=999999)), "Pipeline run doesn't exist")

        with patch("dataportal.graphql.queries.get_file_list", return_value=(False, [])):
            self.assertEqual(query.resolve_files(info_unrestricted, path="/tmp", recursive=False), [])

        with patch(
            "dataportal.graphql.queries.get_file_list",
            return_value=(
                True,
                [
                    {"fileName": "a.ar", "path": "/tmp/a.ar", "fileSize": 10, "isDirectory": False},
                    {"fileName": "b.txt", "path": "/tmp/b.txt", "fileSize": 11, "isDirectory": False},
                ],
            ),
        ):
            files = query.resolve_files(info_unrestricted, path="/tmp", recursive=True)
            self.assertEqual(len(files), 2)

        with patch("dataportal.graphql.queries.PulsarFoldResult.objects.get", return_value=self.public_fold_result):
            with patch(
                "dataportal.graphql.queries.get_file_list",
                return_value=(
                    True,
                    [
                        {"fileName": "x.ar", "path": "/J/x.ar", "fileSize": 10, "isDirectory": False},
                        {"fileName": "dir", "path": "/J/dir", "fileSize": 0, "isDirectory": True},
                    ],
                ),
            ):
                single = query.resolve_file_single_list(
                    info_unrestricted,
                    main_project="MeerTIME",
                    jname=self.pulsar.name,
                    utc=self.public_observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                    beam=self.public_observation.beam,
                )
                self.assertEqual(len(single), 1)

        disabled_main_project = MainProject.objects.create(name="MONSPSR", telescope=self.telescope)
        disabled_project = Project.objects.create(
            code="SCI-DISABLED-001",
            short="DISABLED",
            main_project=disabled_main_project,
            embargo_period=timedelta(days=0),
            allow_downloads=False,
        )
        self.public_observation.project = disabled_project

        disabled_file_list = (
            True,
            [{"fileName": "disabled.ar", "path": "/J/disabled.ar", "fileSize": 10, "isDirectory": False}],
        )
        with (
            patch("dataportal.graphql.queries.PulsarFoldResult.objects.get", return_value=self.public_fold_result),
            patch("dataportal.graphql.queries.get_file_list", return_value=disabled_file_list),
        ):
            disabled_files = query.resolve_file_single_list(
                info_unrestricted,
                main_project="MONSPSR",
                jname=self.pulsar.name,
                utc=self.public_observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
                beam=self.public_observation.beam,
            )
            self.assertEqual(disabled_files, [])
        self.public_observation.project = self.public_project

        with patch(
            "dataportal.graphql.queries.get_file_list",
            return_value=(
                True,
                [{"fileName": "x.ar", "path": "/J/x.ar", "fileSize": 10, "isDirectory": False}],
            ),
        ):
            pulsar_files = query.resolve_file_pulsar_list(
                info_unrestricted,
                main_project="MeerTIME",
                jname=self.pulsar.name,
            )
            self.assertEqual(len(pulsar_files), 1)

        with patch("dataportal.graphql.queries.get_file_list", return_value=(False, [])):
            pulsar_files = query.resolve_file_pulsar_list(
                info_unrestricted,
                main_project="MeerTIME",
                jname=self.pulsar.name,
            )
            self.assertEqual(pulsar_files, [])

        with patch("dataportal.graphql.queries.get_file_list", return_value=disabled_file_list):
            pulsar_files = query.resolve_file_pulsar_list(
                info_unrestricted,
                main_project="MONSPSR",
                jname=self.pulsar.name,
            )
        self.assertEqual(pulsar_files, [])

    def test_queryset_classmethods_in_query_nodes(self):
        info_member = make_info(self.user)
        info_super = make_info(self.superuser)

        self.assertEqual(
            queries.EphemerisNode.get_queryset(Ephemeris.objects.all(), info_super).count(),
            Ephemeris.objects.count(),
        )
        self.assertEqual(
            queries.TemplateNode.get_queryset(Template.objects.all(), info_super).count(),
            Template.objects.count(),
        )
        self.assertEqual(
            queries.ObservationNode.get_queryset(Observation.objects.all(), info_super).count(),
            Observation.objects.count(),
        )
        self.assertEqual(
            queries.PipelineRunNode.get_queryset(PipelineRun.objects.all(), info_super).count(),
            PipelineRun.objects.count(),
        )
        self.assertEqual(
            queries.PulsarFoldResultNode.get_queryset(PulsarFoldResult.objects.all(), info_super).count(),
            PulsarFoldResult.objects.count(),
        )
        self.assertEqual(
            queries.PipelineImageNode.get_queryset(PipelineImage.objects.all(), info_member).count(),
            0,
        )
        self.assertEqual(
            queries.ToaNode.get_queryset(Toa.objects.all(), info_super).count(),
            Toa.objects.count(),
        )

    def test_fold_connection_description_and_project_counts(self):
        iterable = PulsarFoldResult.objects.filter(id__in=[self.private_fold_result.id, self.public_fold_result.id])
        conn = SimpleNamespace(iterable=iterable, edges=[SimpleNamespace(node=self.private_fold_result)])
        self.assertEqual(queries.PulsarFoldResultConnection.resolve_description(conn, None), self.pulsar.comment)
        self.assertEqual(queries.PulsarFoldResultConnection.resolve_total_observations(conn, None), 1)
        self.assertGreater(queries.PulsarFoldResultConnection.resolve_total_observation_hours(conn, None), 0)
        self.assertEqual(queries.PulsarFoldResultConnection.resolve_total_projects(conn, None), 2)

        empty = SimpleNamespace(iterable=[], edges=[])
        self.assertIsNone(queries.PulsarFoldResultConnection.resolve_description(empty, None))

    def test_accessible_ephemeris_and_template_do_not_skip_projectless_pfr(self):
        pipeline_run_id = 9991
        fake_pfr = SimpleNamespace(
            observation=SimpleNamespace(project=None),
            pipeline_run=SimpleNamespace(
                id=pipeline_run_id,
                ephemeris_id=self.private_ephemeris.id,
                template_id=self.private_template.id,
                ephemeris=self.private_ephemeris,
                template=self.private_template,
                created_at=self.now,
            ),
            pipeline_run_id=pipeline_run_id,
        )

        class FakeQS:
            def __iter__(self):
                return iter([fake_pfr])

            def annotate(self, **kwargs):
                return self

            def all(self):
                return self

            def filter(self, **kwargs):
                return self

        class FakeValuesList:
            def distinct(self):
                return [pipeline_run_id]

        class FakeToaFilterResult:
            def values_list(self, *args, **kwargs):
                return FakeValuesList()

        class FakeIdValues:
            def __init__(self, ids):
                self.ids = ids

            def values_list(self, *args, **kwargs):
                return self.ids

        class FakeAccessible:
            def __init__(self, ids):
                self.ids = ids

            def filter(self, **kwargs):
                return FakeIdValues(self.ids)

        conn = SimpleNamespace()
        instance = SimpleNamespace(variable_values={}, context=SimpleNamespace(user=self.unrestricted_user))
        with (
            patch("dataportal.graphql.queries.PulsarFoldResult.objects.select_related", return_value=FakeQS()),
            patch("dataportal.graphql.queries.Toa.objects.filter", return_value=FakeToaFilterResult()),
            patch(
                "dataportal.graphql.queries.Ephemeris.objects.accessible_to",
                return_value=FakeAccessible([self.private_ephemeris.id]),
            ),
            patch(
                "dataportal.graphql.queries.Template.objects.accessible_to",
                return_value=FakeAccessible([self.private_template.id]),
            ),
        ):
            epi = queries.PulsarFoldResultConnection._get_accessible_ephemeris_pfr(conn, instance)
            tmpl = queries.PulsarFoldResultConnection._get_accessible_template_pfr(conn, instance)
            self.assertEqual(epi, (self.private_ephemeris, fake_pfr, True))
            self.assertEqual(tmpl, (self.private_template, fake_pfr, True))
