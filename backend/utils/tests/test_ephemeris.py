import os
import json

from utils.ephemeris import parse_ephemeris_file, convert_frequency_to_period, convert_to_float_if_possible

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


def test_ephemeris_parse():
    tests = [
        # Test a files
        ("ephem_J1705-1903.eph", "ephem_J1705-1903.json"),
        ("ephem_J0437-4715.par", "ephem_J0437-4715.json"),
        ("ephem_J1327-0755.par", "ephem_J1327-0755.json"),
        # Test a string
        (
            "PSRJ           J1705-1903\n"
            "RAJ             17:05:43.8486324         1  0.00000548050814133282\n"
            "DECJ           -19:03:41.41717           1  0.00055777912502136273\n"
            "F0             403.17844297262159661     1  0.00000000000301509692\n"
            "F1             -3.4923240886648697207e-15 1  1.0983876365856974109e-19\n"
            "PEPOCH         59088\n"
            "POSEPOCH       59088\n"
            "DMEPOCH        59000\n"
            "DM             58.504078300843655062     1  0.00026430065604471083\n"
            "DM1            0.0010345206561935254609  1  0.00006010426897540625\n"
            "PMRA           -0.98244727280490175384   1  0.08678389865427849221\n"
            "PMDEC          -4.3758093837499179302    1  0.62766300680811937251\n"
            "PX             -0.3486569736684584694    1  0.11895058319658168011\n"
            "BINARY         ELL1\n"
            "FB0            6.291970592871658366e-05  1  0.00000000021338988441\n"
            "FB1            -2.4915298403920358929e-17 1  3.7170433357456954128e-18\n"
            "FB2            3.3150129969443275417e-25 1  4.8382733167112787341e-26\n"
            "FB3            -2.947491562504159572e-33 1  4.1831926138203372427e-34\n"
            "FB4            1.3137218883763344151e-41 1  1.8018615052759107877e-42\n"
            "A1             0.10436094400773116808    1  0.00000006740420080843\n"
            "TASC           56582.223981204730023     1  0.00179613715288253297\n"
            "EPS1           2.2522925917868801688e-05 1  0.00000129612909923721\n"
            "EPS2           -1.9204141672989537069e-06 1  0.00000115922628371636\n"
            "START          58693.785465305599651\n"
            "FINISH         59760.762666966884925\n"
            "TRACK          -2                           0.00085115976857252328\n"
            "TZRMJD         59233.214201168854888\n"
            "TZRFRQ         1113.9042111000001114\n"
            "TZRSITE        meerkat\n"
            "FD1            -4.0763259943819326546e-06 1  0.00000142628154999764\n"
            "TRES           1.088\n"
            "EPHVER         5\n"
            "NE_SW          4\n"
            "CLK            TT(BIPM2019)\n"
            "MODE 1\n"
            "UNITS          TCB\n"
            "TIMEEPH        IF99\n"
            "DILATEFREQ     Y\n"
            "PLANET_SHAPIRO -1\n"
            "T2CMETHOD      IAU2000B\n"
            "CORRECT_TROPOSPHERE  Y\n"
            "EPHEM          DE438\n"
            "NITS           1\n"
            "NTOA           924\n"
            "CHI2R          15.2535 904\n"
            "JUMP -MJD_58526_59621_1K -1 -1.1962616822e-06 0\n"
            "JUMP -MJD_58550_58690_1K -1 -0.000306243 0\n"
            "JUMP -MJD_58526.21089_1K -1 -2.4628e-05 0\n"
            "JUMP -MJD_58550.14921_1K -1 2.463e-05 0\n"
            "JUMP -MJD_58550.14921B_1K -1 -1.196e-06 0\n"
            "JUMP -MJD_58557.14847_1K -1 -4.785e-06 0\n"
            "JUMP -MJD_58575.9591_1K -1 5.981308411e-07 0",
            "ephem_J1705-1903_string.json",
        ),
    ]
    for test_ephem, expected_json in tests:
        if "string" not in expected_json:
            test_ephem = os.path.join(TEST_DATA_DIR, test_ephem)
        print(f"Testing {test_ephem}")
        ephemeris_dict = parse_ephemeris_file(test_ephem)
        print(json.dumps(ephemeris_dict, indent=4))
        with open(os.path.join(TEST_DATA_DIR, expected_json), 'r') as f:
            expected_dict = json.load(f)
        assert ephemeris_dict == expected_dict
