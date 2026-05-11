import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from graphql import GraphQLError

from dataportal.models import (
    Badge,
    Calibration,
    Ephemeris,
    MainProject,
    Observation,
    ObservationSummary,
    PipelineImage,
    PipelineRun,
    Project,
    ProjectMembership,
    ProjectMembershipRequest,
    Pulsar,
    PulsarFoldResult,
    PulsarFoldSummary,
    PulsarSearchSummary,
    Telescope,
    Template,
    Toa,
    default_ephemeris_end,
    default_ephemeris_start,
)

User = get_user_model()


class ModelsCoverageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = timezone.now()
        cls.user = User.objects.create_user(username="member", email="member@test.com", password="testpass123")
        cls.superuser = User.objects.create_superuser("admin", "admin@test.com", "testpass123")
        cls.other_user = User.objects.create_user(username="other", email="other@test.com", password="testpass123")

        cls.telescope = Telescope.objects.create(name="Scope")
        cls.main_project = MainProject.objects.create(name="MeerTIME", telescope=cls.telescope)
        cls.project = Project.objects.create(
            code="SCI-TEST-001",
            short="PTA",
            main_project=cls.main_project,
            embargo_period=timedelta(days=365),
        )
        cls.public_project = Project.objects.create(
            code="SCI-TEST-002",
            short="TPA",
            main_project=cls.main_project,
            embargo_period=timedelta(days=0),
        )
        cls.pulsar = Pulsar.objects.create(name="J0000+0000", comment="test pulsar")
        cls.calibration = Calibration.objects.create(schedule_block_id="cal-01", calibration_type="pre")

        cls.ephemeris = Ephemeris.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            created_by=cls.user,
            ephemeris_data=json.dumps({"DM": 12.3, "P0": 0.5}),
            p0=0.5,
            dm=12.3,
            valid_from=cls.now - timedelta(days=1),
            valid_to=cls.now + timedelta(days=1),
        )
        cls.template = Template.objects.create(
            pulsar=cls.pulsar,
            project=cls.project,
            band="LBAND",
            created_by=cls.user,
            template_hash="hash-1",
        )
        cls.observation = Observation.objects.create(
            pulsar=cls.pulsar,
            telescope=cls.telescope,
            project=cls.project,
            calibration=cls.calibration,
            ephemeris=cls.ephemeris,
            utc_start=cls.now - timedelta(days=1),
            frequency=1400.0,
            bandwidth=400.0,
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
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )
        cls.pipeline_run = PipelineRun.objects.create(
            observation=cls.observation,
            ephemeris=cls.ephemeris,
            template=cls.template,
            pipeline_name="meerpipe",
            pipeline_version="1.0.0",
            created_by="tester",
            location="/tmp",
            job_state="Completed",
            dm=1.0,
            dm_err=0.1,
            dm_epoch=1.0,
            dm_chi2r=1.0,
            dm_tres=1.0,
            sn=20.0,
            flux=2.0,
            rm=3.0,
            rm_err=0.3,
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
            archive="a.ar",
            freq_MHz=1400.0,
            mjd=59000.0,
            mjd_err=0.001,
            telescope="Scope",
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=16,
            obs_npol=2,
            chan=1,
            subint=1,
            snr=10.0,
        )
        cls.badge = Badge.objects.create(name="Low SNR")
        cls.pipeline_image = PipelineImage.objects.create(
            pulsar_fold_result=cls.fold_result,
            url="https://example.com/image.png",
            cleaned=True,
            image_type="phase-freq",
            resolution="high",
        )

    def test_basic_helpers_and_str_methods(self):
        self.assertEqual(default_ephemeris_start().timestamp(), 0)
        self.assertEqual(default_ephemeris_end().timestamp(), 4294967295)
        self.assertEqual(str(self.pulsar), self.pulsar.name)
        self.assertEqual(str(self.telescope), self.telescope.name)
        self.assertEqual(str(self.main_project), self.main_project.name)
        self.assertEqual(str(self.project), f"{self.project.code}_{self.project.short}")
        self.assertIn(
            self.user.username, str(ProjectMembership.objects.create(user=self.user, project=self.public_project))
        )
        self.assertIn(
            "requested at",
            str(ProjectMembershipRequest.objects.create(user=self.other_user, project=self.public_project)),
        )
        self.assertEqual(str(self.badge), self.badge.name)
        self.assertEqual(str(self.calibration), f"{self.calibration.id}_{self.calibration.schedule_block_id}")
        self.assertEqual(str(self.observation), f"{self.observation.utc_start} {self.observation.beam}")
        self.assertEqual(Pulsar.get_query(name=self.pulsar.name).count(), 1)
        self.assertEqual(Toa.get_query(id=self.toa.id).count(), 1)

    def test_request_to_join_handles_create_exception(self):
        with patch("dataportal.models.ProjectMembershipRequest.objects.create", side_effect=RuntimeError("boom")):
            result = ProjectMembershipRequest.request_to_join(self.other_user, self.project, "hi")

        self.assertFalse(result["success"])
        self.assertIsNone(result["request"])
        self.assertIn("Something went wrong", result["error"])

    def test_membership_approval_requests_superuser_and_permission_error(self):
        req = ProjectMembershipRequest.objects.create(user=self.other_user, project=self.project)
        qs = ProjectMembershipRequest.membership_approval_requests(self.superuser)
        self.assertIn(req, qs)

        with self.assertRaises(GraphQLError):
            ProjectMembershipRequest.membership_approval_requests(self.user)

    def test_queryset_accessible_to_superuser_paths(self):
        self.assertEqual(Observation.objects.accessible_to(self.superuser).count(), Observation.objects.count())
        self.assertEqual(Template.objects.accessible_to(self.superuser).count(), Template.objects.count())
        self.assertEqual(Ephemeris.objects.accessible_to(self.superuser).count(), Ephemeris.objects.count())
        self.assertEqual(PipelineRun.objects.accessible_to(self.superuser).count(), PipelineRun.objects.count())
        self.assertEqual(
            PulsarFoldResult.objects.accessible_to(self.superuser).count(), PulsarFoldResult.objects.count()
        )
        self.assertEqual(PipelineImage.objects.accessible_to(self.superuser).count(), PipelineImage.objects.count())

    def test_ephemeris_clean_validation_error(self):
        bad = Ephemeris(
            pulsar=self.pulsar,
            project=self.project,
            created_by=self.user,
            ephemeris_data=json.dumps({"DM": 1.0, "P0": 0.1}),
            p0=0.1,
            dm=1.0,
            valid_from=self.now,
            valid_to=self.now - timedelta(seconds=1),
        )
        with self.assertRaises(ValidationError):
            bad.clean()

    def test_observation_summary_update_or_create_edge_paths(self):
        none_summary, created = ObservationSummary.update_or_create(
            obs_type="search",
            pulsar=Pulsar.objects.create(name="J9999+9999"),
            main_project=self.main_project,
            project=self.project,
            calibration=self.calibration,
            band="LBAND",
        )
        self.assertIsNone(none_summary)
        self.assertFalse(created)

        with patch("dataportal.models.Observation.objects.filter") as mocked_filter:
            fake_qs = Mock()
            fake_qs.__len__ = Mock(return_value=1)
            fake_qs.order_by.return_value.first.return_value = SimpleNamespace(utc_start=self.now, duration=10)
            fake_qs.order_by.return_value.last.return_value = SimpleNamespace(utc_start=self.now, duration=10)
            fake_qs.values_list.return_value.distinct.return_value = [self.pulsar.name]
            fake_qs.aggregate.side_effect = [{"total": 3600}, ZeroDivisionError()]
            mocked_filter.return_value = fake_qs

            with patch("dataportal.models.ObservationSummary.objects.update_or_create") as mocked_uoc:
                summary = ObservationSummary(
                    pulsar=self.pulsar,
                    main_project=self.main_project,
                    project=self.project,
                    calibration=self.calibration,
                    obs_type="fold",
                    band="LBAND",
                )
                mocked_uoc.return_value = (summary, False)
                updated, created = ObservationSummary.update_or_create(
                    obs_type="fold",
                    pulsar=self.pulsar,
                    main_project=self.main_project,
                    project=self.project,
                    calibration=self.calibration,
                    band="LBAND",
                )
                self.assertFalse(created)
                self.assertEqual(updated.pulsar, self.pulsar)

    def test_fold_and_search_summary_query_helpers_and_early_returns(self):
        self.assertGreaterEqual(PulsarFoldSummary.get_query(main_project="All").count(), 0)
        self.assertGreaterEqual(PulsarSearchSummary.get_query(main_project="All").count(), 0)

        obs_a = SimpleNamespace(project=SimpleNamespace(short="PTA"))
        obs_b = SimpleNamespace(project=SimpleNamespace(short="TPA"))
        obs_c = SimpleNamespace(project=SimpleNamespace(short="PTA"))
        self.assertEqual(PulsarFoldSummary.get_most_common_project([obs_a, obs_b, obs_c]), "PTA")
        self.assertEqual(PulsarSearchSummary.get_most_common_project([obs_a, obs_b, obs_c]), "PTA")

        new_pulsar = Pulsar.objects.create(name="J1111+1111")
        self.assertIsNone(PulsarFoldSummary.update_or_create(new_pulsar, self.main_project))

        search_obs = Observation.objects.create(
            pulsar=new_pulsar,
            telescope=self.telescope,
            project=self.public_project,
            calibration=self.calibration,
            utc_start=self.now - timedelta(days=2),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=2,
            nant=32,
            nant_eff=30,
            npol=2,
            obs_type="search",
            raj="00:00:00",
            decj="-00:00:00",
            duration=120.0,
            nbit=8,
            tsamp=0.001,
        )
        PulsarSearchSummary.update_or_create(new_pulsar, self.main_project)
        search_obs.duration = 240.0
        search_obs.save()
        summary, created = PulsarSearchSummary.update_or_create(new_pulsar, self.main_project)
        self.assertFalse(created)
        self.assertEqual(summary.pulsar, new_pulsar)

        fold_summary = PulsarFoldSummary.objects.create(
            pulsar=new_pulsar,
            main_project=self.main_project,
            first_observation=self.now - timedelta(days=1),
            latest_observation=self.now,
            latest_observation_beam=1,
            timespan=2,
            number_of_observations=2,
            total_integration_hours=1.0,
            last_integration_minutes=2.0,
            all_bands="LBAND",
            last_sn=1.0,
            highest_sn=1.0,
            lowest_sn=1.0,
            avg_sn_pipe=1.0,
            max_sn_pipe=1.0,
            most_common_project=self.public_project.short,
            all_projects=self.public_project.short,
        )
        search_summary, _ = PulsarSearchSummary.objects.update_or_create(
            pulsar=new_pulsar,
            main_project=self.main_project,
            defaults={
                "first_observation": self.now - timedelta(days=1),
                "latest_observation": self.now,
                "timespan": 2,
                "number_of_observations": 2,
                "total_integration_hours": 1.0,
                "last_integration_minutes": 2.0,
                "all_bands": "LBAND",
                "most_common_project": self.public_project.short,
                "all_projects": self.public_project.short,
            },
        )
        self.assertIn(
            fold_summary,
            PulsarFoldSummary.get_query(
                band="LBAND",
                most_common_project=self.public_project.short,
                project=self.public_project.short,
                main_project=self.main_project.name,
            ),
        )
        self.assertIn(
            search_summary,
            PulsarSearchSummary.get_query(
                band="LBAND",
                most_common_project=self.public_project.short,
                project=self.public_project.short,
                main_project=self.main_project.name,
            ),
        )

    def test_fold_summary_returns_when_last_result_or_pipeline_run_missing(self):
        new_pulsar = Pulsar.objects.create(name="J2222+2222")
        obs = Observation.objects.create(
            pulsar=new_pulsar,
            telescope=self.telescope,
            project=self.public_project,
            calibration=self.calibration,
            ephemeris=self.ephemeris,
            utc_start=self.now - timedelta(hours=2),
            frequency=1400.0,
            bandwidth=400.0,
            nchan=1024,
            beam=3,
            nant=32,
            nant_eff=30,
            npol=2,
            obs_type="fold",
            raj="00:00:00",
            decj="-00:00:00",
            duration=180.0,
            nbit=8,
            tsamp=0.001,
            fold_nbin=128,
            fold_nchan=128,
            fold_tsubint=10,
        )
        self.assertIsNone(PulsarFoldSummary.update_or_create(new_pulsar, self.main_project))

        pr = PipelineRun.objects.create(
            observation=obs,
            ephemeris=self.ephemeris,
            template=self.template,
            pipeline_name="meerpipe",
            pipeline_version="1.0.0",
            created_by="tester",
            location="/tmp",
            job_state="Completed",
            sn=5.0,
            dm=10.0,
            percent_rfi_zapped=0.0,
        )
        PulsarFoldResult.objects.create(observation=obs, pipeline_run=pr, pulsar=new_pulsar)
        summary, created = PulsarFoldSummary.update_or_create(new_pulsar, self.main_project)
        self.assertIsNotNone(summary)
        self.assertIn(created, [True, False])

    def test_toa_restriction_and_bulk_create_error_paths(self):
        self.assertTrue(self.toa.is_restricted(self.other_user))
        self.assertTrue(self.toa.is_restricted(SimpleNamespace(is_authenticated=False, is_superuser=False)))

        ProjectMembership.objects.create(user=self.other_user, project=self.project, is_active=True)
        self.assertFalse(self.toa.is_restricted(self.other_user))

        with patch("dataportal.models.parse_ephemeris_file") as mock_parse:
            mock_parse.return_value = {
                "P0": 0.5,
                "DM": 12.3,
                "START": (self.now - timedelta(days=1)).isoformat(),
                "FINISH": (self.now + timedelta(days=1)).isoformat(),
            }
            with patch("dataportal.models.Ephemeris.objects.get_or_create", side_effect=IntegrityError):
                with patch("dataportal.models.Ephemeris.objects.get", return_value=self.ephemeris) as mock_get:
                    created = Toa.bulk_create(
                        pipeline_run_id=self.pipeline_run.id,
                        project_short=self.project.short,
                        template_id=self.template.id,
                        ephemeris_text="FAKE",
                        toa_lines=["FORMAT 1\n"],
                        dm_corrected=False,
                        nsub_type="1",
                        npol=2,
                        nchan=16,
                    )
                    self.assertEqual(created, [])
                    self.assertTrue(mock_get.called)

        with patch(
            "dataportal.models.parse_ephemeris_file",
            return_value={
                "P0": 0.5,
                "DM": 12.3,
                "START": (self.now - timedelta(days=1)).isoformat(),
                "FINISH": (self.now + timedelta(days=1)).isoformat(),
            },
        ):
            with patch("dataportal.models.toa_line_to_dict", return_value={"archive": "x"}):
                with patch("dataportal.models.toa_dict_to_line", return_value="different"):
                    with self.assertRaises(GraphQLError):
                        Toa.bulk_create(
                            pipeline_run_id=self.pipeline_run.id,
                            project_short=self.project.short,
                            template_id=self.template.id,
                            ephemeris_text="FAKE",
                            toa_lines=["abc\n"],
                            dm_corrected=False,
                            nsub_type="1",
                            npol=2,
                            nchan=16,
                        )
