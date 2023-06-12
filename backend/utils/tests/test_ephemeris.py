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
    tests = [
        # Test a file
        os.path.join(TEST_DATA_DIR, "ephem_J1705-1903.eph"),
        # Test a string
        "PSRJ \t J1705-1903\nRAJ  \t  17:05:43.8502743  \t  2.846e-4\nDECJ  \t  -19:03:41.32025  \t  3.999e-2\nF0  \t  403.17844370811329346  \t  1.289e-9\nDM  \t  57.50571096535851744  \t  5.052e-5\nF1  \t  -3.4428715379610950e-15  \t  6.438e-18\nPEPOCH  \t  56618  \t  \nPOSEPOCH  \t  56618  \t  \nDMEPOCH  \t  56618  \t  \nPMRA  \t  -4.3811121114291140e+0  \t  1.3305\nPMDEC  \t  -1.7888684789156335e+1  \t  13.2010\nPX  \t  0  \t  \nBINARY  \t  ELL1  \t  \nPB  \t  0.18395403344503906874  \t  3.598e-8\nA1  \t  0.10436244224177347356  \t  1.698e-6\nPBDOT  \t  -3.7178429899716451e-12  \t  1.539e-11\nTASC  \t  56582.21217308180756000000  \t  2.285e-4\nEPS1  \t  7.9300304759274633e-5  \t  1.779e-5\nEPS2  \t  -3.3596418853323134e-5  \t  7.178e-6\nTZRMJD  \t  58855.25408581254015800000  \t  \nTZRFRQ  \t  944.52099999999995816000  \t  \nTZRSITE  \t  meerkat  \t  \nEPHVER  \t  5  \t  \nCLK  \t  TT(TAI)  \t  \nUNITS  \t  TCB  \t  \nTIMEEPH  \t  IF99  \t  \nT2CMETHOD  \t  IAU2000B  \t  \nCORRECT_TROPOSPHERE  \t  N  \t  \nEPHEM  \t  DE421  \t  \n",
    ]
    for test_ephem in tests:
        ephemeris_dict = parse_ephemeris_file(test_ephem)
        # TODO actually test something