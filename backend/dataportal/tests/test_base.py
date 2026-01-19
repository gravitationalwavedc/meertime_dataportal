"""
Base test classes for the dataportal app.

This module provides base test classes that handle common setup/teardown,
particularly for isolating file system operations during parallel test execution.
"""

import tempfile
from django.test import TestCase, override_settings


class BaseTestCaseWithTempMedia(TestCase):
    """
    Base test class that provides isolated temporary directories for MEDIA_ROOT
    and MEERTIME_DATA_DIR to prevent race conditions during parallel test execution.

    Django parallelizes test classes (not methods within a class), so class-level
    setup/teardown ensures each test class gets its own isolated file system space.

    Usage:
        class MyTestCase(BaseTestCaseWithTempMedia):
            def setUp(self):
                super().setUp()
                # Your test setup here

            def test_something(self):
                # Test that may write to MEDIA_ROOT or MEERTIME_DATA_DIR
                pass
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create temporary directories for this test class
        cls._temp_media_dir = tempfile.TemporaryDirectory()
        cls._temp_meertime_data_dir = tempfile.TemporaryDirectory()

        # Override settings for the entire test class
        cls._settings_override = override_settings(
            MEDIA_ROOT=cls._temp_media_dir.name, MEERTIME_DATA_DIR=cls._temp_meertime_data_dir.name
        )
        cls._settings_override.enable()

    @classmethod
    def tearDownClass(cls):
        # Disable settings override
        cls._settings_override.disable()

        # Clean up temporary directories
        cls._temp_media_dir.cleanup()
        cls._temp_meertime_data_dir.cleanup()

        super().tearDownClass()
