import os

from django.test import TestCase, TransactionTestCase

from dataportal.models import Badge, Calibration, PipelineRun, Toa
from dataportal.tests.testing_utils import create_basic_data, create_observation_pipeline_run_toa, setup_query_test

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")


class BadgeTestCase(TestCase):
    def test_rfi_badge(self):
        client, user, telescope, project, ephemeris, template, pipeline_run, observation, cal = setup_query_test()

        # Create RFI badge
        rfi_badge, created = Badge.objects.get_or_create(
            name="Strong RFI",
            description="Over 20% of RFI removed from observation",
        )

        # PipelineRun created in setup_query_test has 10% Rfi so should not have an RFI badge
        self.assertLess(pipeline_run.percent_rfi_zapped, 0.2)
        self.assertNotIn(rfi_badge, pipeline_run.badges.all())

        # Make a PipelineRun with 30% Rfi so should have an RFI badge
        pipeline_run = PipelineRun.objects.create(
            observation=observation,
            ephemeris=ephemeris,
            template=template,
            pipeline_name="meerpipe",
            pipeline_description="MeerTime pipeline",
            pipeline_version="3.0.0",
            created_by="test",
            job_state="Completed",
            location="/test/location",
            dm=20.0,
            dm_err=1.0,
            dm_epoch=1.0,
            dm_chi2r=1.0,
            dm_tres=1.0,
            sn=100.0,
            flux=25.0,
            rm=10.0,
            rm_err=1.0,
            percent_rfi_zapped=0.3,
        )
        self.assertGreater(pipeline_run.percent_rfi_zapped, 0.2)
        self.assertIn(rfi_badge, pipeline_run.badges.all())

    def test_rm_badge(self):
        telescope, project, ephemeris, template = create_basic_data()

        # Create RM badge
        rm_badge, created = Badge.objects.get_or_create(
            name="RM Drift",
            description="The Rotation Measure has drifted three weighted standard deviations from the weighted mean",
        )

        # Create five Pipeline runs with one RM values over 3 STD away from the mean
        _, _, pr1 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"),
            telescope,
            template,
            rm=10.0,
            rm_err=0.1,
        )
        _, _, pr2 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"),
            telescope,
            template,
            rm=10.1,
            rm_err=0.1,
        )
        _, _, pr3 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
            telescope,
            template,
            rm=10.2,
            rm_err=0.1,
        )
        # Check no badges at this point
        self.assertEqual(pr1.badges.filter(id=rm_badge.id).count(), 0)
        self.assertEqual(pr2.badges.filter(id=rm_badge.id).count(), 0)
        self.assertEqual(pr3.badges.filter(id=rm_badge.id).count(), 0)
        _, _, pr4 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-12-15-17:22:31_1_J0125-2327.json"),
            telescope,
            template,
            rm=200.0,
            rm_err=10,
        )
        _, _, pr5 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-12-15-17:22:31_1_J0125-2327.json"),
            telescope,
            template,
            rm=10.3,
            rm_err=0.1,
        )
        # And one with a None RM
        _, _, pr6 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-12-15-17:22:31_1_J0125-2327.json"),
            telescope,
            template,
            rm=None,
            rm_err=None,
        )
        # Test only the last obs has the badge
        self.assertEqual(pr1.badges.filter(id=rm_badge.id).count(), 0)
        self.assertEqual(pr2.badges.filter(id=rm_badge.id).count(), 0)
        self.assertEqual(pr3.badges.filter(id=rm_badge.id).count(), 0)
        self.assertEqual(pr4.badges.filter(id=rm_badge.id).count(), 1)
        self.assertEqual(pr5.badges.filter(id=rm_badge.id).count(), 0)
        self.assertEqual(pr6.badges.filter(id=rm_badge.id).count(), 0)

    def test_dm_badge(self):
        telescope, project, ephemeris, template = create_basic_data()
        dm_badge, created = Badge.objects.get_or_create(
            name="DM Drift",
            description="The DM has drifted away from the median DM of the pulsar enough to cause a dispersion of three profile bins",  # noqa
        )

        # Create for three pipeline runs where one is over 0.001 DM away from the median which will be more than 1 bin
        _, _, pr1 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-04-23-06:11:30_1_J0125-2327.json"),
            telescope,
            template,
            dm=10.000,
        )
        _, _, pr2 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2019-05-14-10:14:18_1_J0125-2327.json"),
            telescope,
            template,
            dm=10.0005,
        )
        _, _, pr3 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
            telescope,
            template,
            dm=11.002,
        )
        # And one with a None DM
        _, _, pr4 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
            telescope,
            template,
            dm=None,
        )
        # Test only last pr has badge
        self.assertEqual(pr1.badges.filter(id=dm_badge.id).count(), 0)
        self.assertEqual(pr2.badges.filter(id=dm_badge.id).count(), 0)
        self.assertEqual(pr3.badges.filter(id=dm_badge.id).count(), 1)
        self.assertEqual(pr4.badges.filter(id=dm_badge.id).count(), 0)


# Using TransactionTestCase for this test as it might require transaction management
class SessionTimingJumpBadgeTestCase(TransactionTestCase):
    def test_session_timing_jump_badge(self):
        telescope, project, ephemeris, template = create_basic_data()

        # Create Session Timing Jump badge
        timing_jump_badge, created = Badge.objects.get_or_create(
            name="Session Timing Jump",
            description="Observed jump in ToA residuals of all observations of this session",
        )

        # Create a calibration (session) with two observations loaded from JSON files below
        calibration = Calibration.objects.create(
            schedule_block_id="20000101-0BAD",
            calibration_type="pre",
            location=None,
        )

        # Create observations linked to the calibration
        obs1, _, pr1 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2020-07-10-05:07:28_2_J0125-2327.json"),
            telescope,
            template,
            calibration=calibration,
        )
        obs2, _, pr2 = create_observation_pipeline_run_toa(
            os.path.join(TEST_DATA_DIR, "2023-04-17-15:08:35_1_J0437-4715.json"),
            telescope,
            template,
            calibration=calibration,
        )

        # Simulate a condition where the Session Timing Jump badge should be applied to the calibration (session)
        calibration.badges.add(timing_jump_badge)

        # Verify that the badge is attached to the calibration
        self.assertIn(timing_jump_badge, calibration.badges.all())

        # Verify that the badge is accessible via the observations
        self.assertIn(timing_jump_badge, obs1.calibration.badges.all())
        self.assertIn(timing_jump_badge, obs2.calibration.badges.all())

        # Verify that the badge is accessible via the pipeline runs
        self.assertIn(timing_jump_badge, pr1.observation.calibration.badges.all())
        self.assertIn(timing_jump_badge, pr2.observation.calibration.badges.all())

        # Verify filtering logic: ToAs linked to the calibration should be excluded
        exclude_badges = ["Session Timing Jump"]
        filtered_toas = Toa.objects.exclude(pipeline_run__badges__name__in=exclude_badges).exclude(
            pipeline_run__observation__calibration__badges__name__in=exclude_badges,
        )

        # Ensure no ToAs from the calibration are included in the filtered queryset
        self.assertGreater(obs1.toas.count(), 0)
        self.assertGreater(obs2.toas.count(), 0)
        for toa in obs1.toas.all():
            self.assertNotIn(toa, filtered_toas)
        for toa in obs2.toas.all():
            self.assertNotIn(toa, filtered_toas)
