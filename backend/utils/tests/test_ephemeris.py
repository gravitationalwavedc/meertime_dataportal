import os

from utils.ephemeris import convert_frequency_to_period, convert_to_float_if_possible

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")


def test_period_calculation():
    tests = [
        # Test values of J2355+2246 from ATNF
        ("0.5431872107706268", "8.851570378343201e-11", "1.8409859072", "3e-10"),
    ]
    for f0, f0_err, p0_exp, p0_err_exp in tests:
        p0, p0_err = convert_frequency_to_period(f0, f0_err)
    assert str(p0) == p0_exp
    assert str(p0_err) == p0_err_exp


def test_convert_to_float_if_possible():
    tests = [
        ("J1705-1903", str, "J1705-1903"),
        ("0.00000548050814133282", float, 0.00000548050814133282),
        ("-2.4915298403920358929e-17", float, -2.4915298403920358929e-17),
        ("-2.4915298403920358929E-17", float, -2.4915298403920358929e-17),
        ("-2.4915298403920358929D-17", float, -2.4915298403920358929e-17),
    ]
    for test_value, test_type, expected_value in tests:
        possible_float = convert_to_float_if_possible(test_value)
        assert possible_float == expected_value
        assert isinstance(possible_float, test_type)
