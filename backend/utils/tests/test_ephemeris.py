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
        os.path.join(TEST_DATA_DIR, "ephem_J0437-4715.par"),
        # Test a string
        "PSRJ           J1705-1903\nRAJ             17:05:43.8486324         1  0.00000548050814133282\nDECJ           -19:03:41.41717           1  0.00055777912502136273\nF0             403.17844297262159661     1  0.00000000000301509692\nF1             -3.4923240886648697207e-15 1  1.0983876365856974109e-19\nPEPOCH         59088\nPOSEPOCH       59088\nDMEPOCH        59000\nDM             58.504078300843655062     1  0.00026430065604471083\nDM1            0.0010345206561935254609  1  0.00006010426897540625\nPMRA           -0.98244727280490175384   1  0.08678389865427849221\nPMDEC          -4.3758093837499179302    1  0.62766300680811937251\nPX             -0.3486569736684584694    1  0.11895058319658168011\nBINARY         ELL1\nFB0            6.291970592871658366e-05  1  0.00000000021338988441\nFB1            -2.4915298403920358929e-17 1  3.7170433357456954128e-18\nFB2            3.3150129969443275417e-25 1  4.8382733167112787341e-26\nFB3            -2.947491562504159572e-33 1  4.1831926138203372427e-34\nFB4            1.3137218883763344151e-41 1  1.8018615052759107877e-42\nA1             0.10436094400773116808    1  0.00000006740420080843\nTASC           56582.223981204730023     1  0.00179613715288253297\nEPS1           2.2522925917868801688e-05 1  0.00000129612909923721\nEPS2           -1.9204141672989537069e-06 1  0.00000115922628371636\nSTART          58693.785465305599651\nFINISH         59760.762666966884925\nTRACK          -2                           0.00085115976857252328\nTZRMJD         59233.214201168854888\nTZRFRQ         1113.9042111000001114\nTZRSITE        meerkat\nFD1            -4.0763259943819326546e-06 1  0.00000142628154999764\nTRES           1.088\nEPHVER         5\nNE_SW          4\nCLK            TT(BIPM2019)\nMODE 1\nUNITS          TCB\nTIMEEPH        IF99\nDILATEFREQ     Y\nPLANET_SHAPIRO -1\nT2CMETHOD      IAU2000B\nCORRECT_TROPOSPHERE  Y\nEPHEM          DE438\nNITS           1\nNTOA           924\nCHI2R          15.2535 904\nJUMP -MJD_58526_59621_1K -1 -1.1962616822e-06 0\nJUMP -MJD_58550_58690_1K -1 -0.000306243 0\nJUMP -MJD_58526.21089_1K -1 -2.4628e-05 0\nJUMP -MJD_58550.14921_1K -1 2.463e-05 0\nJUMP -MJD_58550.14921B_1K -1 -1.196e-06 0\nJUMP -MJD_58557.14847_1K -1 -4.785e-06 0\nJUMP -MJD_58575.9591_1K -1 5.981308411e-07 0",
    ]
    for test_ephem in tests:
        ephemeris_dict = parse_ephemeris_file(test_ephem)
        # TODO actually test something