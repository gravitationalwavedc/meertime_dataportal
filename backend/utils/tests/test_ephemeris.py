import os

from utils.ephemeris import parse_ephemeris_file, convert_frequency_to_period


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")


def test_period_calculation():
    tests = [
        # Test values of J2355+2246 from ATNF
        ("0.5431872107706268", "8.851570378343201e-11", "1.8409859072", "3E-10"),
    ]
    for f0, f0_err, p0_exp, p0_err_exp in tests:
        p0, p0_err = convert_frequency_to_period(f0, f0_err)
    assert str(p0)     == p0_exp
    assert str(p0_err) == p0_err_exp


def test_ephemeris_parse():
    ephemeris_dict = parse_ephemeris_file(os.path.join(TEST_DATA_DIR, "ephem_J1705-1903.eph"))
    # TODO actually test something