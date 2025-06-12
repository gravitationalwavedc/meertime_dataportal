from django.test import TestCase

from utils.observing_bands import get_band


class ObservingBandsTestCase(TestCase):
    """Test case for observing bands utility functions."""

    def test_get_band(self):
        """Test band classification based on frequency and bandwidth."""
        # Test all LBAND frequencies
        self.assertEqual(get_band(1283.5, 856.0), "LBAND")
        self.assertEqual(get_band(1283.4409, 775.75), "LBAND")
        self.assertEqual(get_band(1283.00001, 642.0), "LBAND")
        self.assertEqual(get_band(1283.9999, 0), "LBAND")

        # Test UHF min/max frequencies
        self.assertEqual(get_band(815.0001, 544.0), "UHF")
        self.assertEqual(get_band(815.9999, 544.0), "UHF")

        # Test SBAND min/max frequencies
        self.assertEqual(get_band(2185.0001, 875.0), "SBAND_0")
        self.assertEqual(get_band(2188.9999, 875.0), "SBAND_0")
        self.assertEqual(get_band(2404.0001, 875.0), "SBAND_1")
        self.assertEqual(get_band(2407.9999, 875.0), "SBAND_1")
        self.assertEqual(get_band(2623.0001, 875.0), "SBAND_2")
        self.assertEqual(get_band(2626.9999, 875.0), "SBAND_2")
        self.assertEqual(get_band(2841.0001, 875.0), "SBAND_3")
        self.assertEqual(get_band(2844.9999, 875.0), "SBAND_3")
        self.assertEqual(get_band(3060.0001, 875.0), "SBAND_4")
        self.assertEqual(get_band(3063.9999, 875.0), "SBAND_4")

        # Test Other
        self.assertEqual(get_band(1000, 475.2), "OTHER")
