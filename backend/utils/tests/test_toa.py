import os

from django.test import TestCase
from utils.toa import toa_line_to_dict, toa_dict_to_line

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

TOA_FILES = [
    (os.path.join(TEST_DATA_DIR, "J1705-1903_2020-12-24-07:06:49_zap.4ch1p12t.ar.tim"), 4),
    (os.path.join(TEST_DATA_DIR, "J1337-6423_2019-07-01-15:12:35_zap.16ch1p1t.ar.dm_corrected.tim"), 16),
    (os.path.join(TEST_DATA_DIR, "J1644-4559_2019-09-06-14:27:14_zap.1ch1p1t.ar.tim"), 1),
    (os.path.join(TEST_DATA_DIR, "J0835-4510_2019-04-17-22:39:05_zap.1ch1p1t.ar.tim"), 1),
    (os.path.join(TEST_DATA_DIR, "J0437-4715_2019-03-26-16:29:52_zap.1ch1p1t.ar.tim"), 1),
    (os.path.join(TEST_DATA_DIR, "J0437-4715_2022-12-02-03:18:27_zap.1ch1p1t.ar.tim"), 1),
    (os.path.join(TEST_DATA_DIR, "J1757-1854_2020-03-08-06:50:57_zap.1ch1p1t.ar.tim"), 1),
    (os.path.join(TEST_DATA_DIR, "J0034-0721_2022-06-29-20:04:33_molonglo.tim"), 1),
]


class ToaTestCase(TestCase):
    """Test case for TOA utility functions."""

    def test_toa_line_to_dict_to_line(self):
        """
        Test that toa_line_to_dict(toa_line_to_str(toa_dict)) == toa_dict
        """
        for toa_file, _ in TOA_FILES:
            with open(toa_file, "r") as f:
                toa_lines = f.readlines()
                for toa_line in toa_lines:
                    if "FORMAT" in toa_line:
                        continue
                    input_toa_line = toa_line.rstrip("\n")
                    toa_dict = toa_line_to_dict(input_toa_line)
                    output_toa_line = toa_dict_to_line(toa_dict)
                    self.assertEqual(input_toa_line, output_toa_line)
