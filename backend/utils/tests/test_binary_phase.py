import pytest
import numpy as np
from utils.binary_phase import get_binary_phase

def test_get_binary_phase():
    tests = [
        (
            58916.326063833455837,
            {
                "PSRJ": "J1915+1606",
                "RAJ": "19:15:27.9980670",
                "RAJ_ERR": 3e-05,
                "DECJ": "+16:06:27.37364",
                "DECJ_ERR": 0.0005,
                "F0": 16.94055165104785,
                "F0_ERR": 3.22225794107241e-06,
                "F1": -2.4733e-15,
                "F1_ERR": 1e-19,
                "PEPOCH": 58774.0,
                "POSEPOCH": 58774.0,
                "DMEPOCH": 58774.0,
                "DM": 168.77,
                "DM_ERR": 0.01,
                "PMRA": -1.23,
                "PMRA_ERR": 0.04,
                "PMDEC": -0.83,
                "PMDEC_ERR": 0.04,
                "BINARY": "DDH",
                "PB": 0.322997448918,
                "PB_ERR": 3e-12,
                "T0": 52144.90097849,
                "T0_ERR": 3e-08,
                "A1": 2.341782,
                "A1_ERR": 3e-06,
                "OM": 292.5445,
                "OM_ERR": 8e-05,
                "ECC": 0.617134,
                "ECC_ERR": 4e-07,
                "EDOT": 6e-16,
                "EDOT_ERR": 7e-16,
                "PBDOT": -2.423e-12,
                "PBDOT_ERR": 1e-15,
                "OMDOT": 4.226585,
                "OMDOT_ERR": 4e-06,
                "GAMMA": 4.307e-06,
                "GAMMA_ERR": 4e-09,
                "START": "2019-10-18T14:34:21.495627Z",
                "FINISH": "2019-10-18T14:37:23.115452Z",
                "TRACK": 1.0,
                "TZRMJD": 58774.60809149166,
                "TZRFRQ": 1309.028,
                "TZRSITE": "meerkat",
                "DTHETA": 4e-06,
                "DTHETA_ERR": 2.5e-06,
                "TRES": 22.675,
                "EPHVER": 5.0,
                "H3": 6e-07,
                "H3_ERR": 1e-07,
                "STIG": 0.38,
                "STIG_ERR": 0.04,
                "CLK": "TT(TAI)",
                "MODE": 1.0,
                "UNITS": "TDB",
                "TIMEEPH": "IF99",
                "DILATEFREQ": "Y",
                "PLANET_SHAPIRO": "Y",
                "T2CMETHOD": "TEMPO",
                "NE_SW": 4.0,
                "CORRECT_TROPOSPHERE": "N",
                "EPHEM": "DE405",
                "NITS": 1.0,
                "NTOA": 6.0,
                "CHI2R": 0.4071,
                "CHI2R_ERR": 4.0,
                "P0": 0.05902995,
                "P0_ERR": 1e-08
            },
            0.47618863436144104315,
        ),
        (
            59000.575333572529996,
            {
                'PSRJ': 'J0348+0432',
                'RAJ': '03:48:43.639000',
                'RAJ_ERR': 4e-06,
                'DECJ': '+04:32:11.4580',
                'DECJ_ERR': 0.0002,
                'F0': 25.5606361937675,
                'F0_ERR': 4e-13,
                'F1': -1.5729e-16,
                'F1_ERR': 3e-20,
                'PEPOCH': 56000.0,
                'POSEPOCH': 56000.0,
                'DMEPOCH': 58605.6102482,
                'DM': 40.46812419596452,
                'DM_ERR': 0.0017732257991533056,
                'PMRA': 4.04,
                'PMRA_ERR': 0.16,
                'PMDEC': 3.5,
                'PMDEC_ERR': 0.6,
                'BINARY': 'ELL1',
                'PB': 0.102424062722,
                'PB_ERR': 7e-12,
                'A1': 0.14097938,
                'A1_ERR': 7e-08,
                'PBDOT': -2.73e-12,
                'PBDOT_ERR': 4.5e-13,
                'TASC': 56000.084771047,
                'TASC_ERR': 1.1e-08,
                'EPS1': 1.9e-06,
                'EPS1_ERR': 1e-06,
                'EPS2': 1.4e-06,
                'EPS2_ERR': 1e-06,
                'M2': 0.172,
                'M2_ERR': 0.003,
                'START': '2020-09-03T04:59:21.177691Z',
                'FINISH': '2020-09-03T04:59:21.216152Z',
                'TZRMJD': 59095.20788422763,
                'TZRFRQ': 1397.27,
                'TZRSITE': 'meerkat',
                'TRES': 13.118,
                'EPHVER': 5.0,
                'CLK': 'TT(TAI)',
                'MODE': 1.0,
                'UNITS': 'TDB',
                'TIMEEPH': 'IF99',
                'DILATEFREQ': 'Y',
                'PLANET_SHAPIRO': 'Y',
                'T2CMETHOD': 'TEMPO',
                'NE_SW': 4.0,
                'CORRECT_TROPOSPHERE': 'N',
                'EPHEM': 'DE405',
                'NITS': 1.0,
                'NTOA': 57.0,
                'CHI2R': 0.683,
                'CHI2R_ERR': 55.0,
                'TIMEOFFSETS': [{'type': 'JUMP',
                'mjd': '-MJD_58550_58690_1K',
                'display': '-0.000306243',
                'offset': '-0.000306243',
                'fit': '-0.000306243'}, {'type': 'JUMP',
                'mjd': '-MJD_58526.21089_1K',
                'display': '-2.4628e-05',
                'offset': '-2.4628e-05',
                'fit': '-2.4628e-05'}, {'type': 'JUMP',
                'mjd': '-MJD_58550.14921_1K',
                'display': '2.463e-05',
                'offset': '2.463e-05',
                'fit': '2.463e-05'}, {'type': 'JUMP',
                'mjd': '-MJD_58550.14921B_1K',
                'display': '-1.196e-06',
                'offset': '-1.196e-06',
                'fit': '-1.196e-06'}, {'type': 'JUMP',
                'mjd': '-MJD_58557.14847_1K',
                'display': '-4.785e-06',
                'offset': '-4.785e-06',
                'fit': '-4.785e-06'}, {'type': 'JUMP',
                'mjd': '-MJD_58575.9591_1K',
                'display': '5.981308411e-07',
                'offset': '5.981308411e-07',
                'fit': '5.981308411e-07'}],
                'P0': 0.0391226569017806,
                'P0_ERR': 6e-16
            },
            0.7829126961863446801,
        ),
        (
            59034.30203633312,
            {
                'PSRJ': 'J0337+1715',
                'RAJ': '03:37:43.82589000',
                'DECJ': '17:15:14.8281000',
                'POSEPOCH': 56337.0,
                'F0': 365.9533436553,
                'F0_ERR': 6.434e-13,
                'F1': '-2.364700000000D-15',
                'PEPOCH': 56100.0,
                'START': '2011-12-22T07:32:09.600000Z',
                'FINISH': '2013-05-24T11:51:21.600000Z',
                'DM': 21.313,
                'SOLARN0': 10.0,
                'EPHEM': 'DE405',
                'CLK': 'UTC(NIST)',
                'NTOA': 26296.0,
                'TRES': 48.49,
                'TZRMJD': 56100.13969898718,
                'TZRFRQ': 1379.999,
                'TZRSITE': 'i',
                'NITS': 9.0,
                'EPHVER': 2.0,
                'BINARY': 'BTX',
                'PLAN': 1.0,
                'A1': 1.217524327,
                'A1_ERR': 1e-08,
                'E': 0.0006761058,
                'E_ERR': 1.54e-08,
                'T0': 55917.576630732,
                'T0_ERR': 6.197e-06,
                'OM': 94.618155415179,
                'OM_ERR': 0.001369420885,
                'FB0': 7.103160894881e-06,
                'FB0_ERR': 2.040170931208e-16,
                'A1_2': 74.668209801,
                'A1_2_ERR': 1.6e-08,
                'E_2': 0.035349165,
                'E_2_ERR': 0.0,
                'T0_2': 56317.233774323,
                'T0_2_ERR': 6.03e-07,
                'PB_2': 327.218955257157,
                'PB_2_ERR': 5.7601e-08,
                'OM_2': 95.725598474693,
                'OM_2_ERR': 6.49604e-07,
                'P0': 0.00273258877760637,
                'P0_ERR': 5e-18
            },
            0.03804283667510119919,
        )
    ]

    for mjd, ephemeris_dict, expected in tests:
        binary_phase = get_binary_phase(np.array([float(mjd)]), ephemeris_dict)[0]
        assert binary_phase == pytest.approx(expected, rel=1e-6)
