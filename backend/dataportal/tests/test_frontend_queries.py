# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meertime.settings.settings')
import pytest
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenClient
from dataportal.tests.testing_utils import create_pulsar_with_observations
from dataportal.models import Telescope


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username="buffy")
    jname = create_pulsar_with_observations()
    return client, user, jname


def create_test_session():
    t = Telescopes.objects.create(name="MeerKat")
    return Sessions.objects.create(
        telescope=t,
        start=FoldPulsarDetail.objects.first().utc,
        end=FoldPulsarDetail.objects.last().utc,
    )@pytest.mark.django_db



@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_query_no_token():
    client, _, _ = setup_query_test()
    response = client.execute(
        """
        query {
            allFoldpulsarsummarys {
                edges {
                    node {
                        id
                    }
                }
            }
        }
    """
    )
    expected_error_message = "You do not have permission to perform this action"
    assert not response.data["allFoldpulsarsummarys"]
    assert response.errors[0].message == expected_error_message

@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_query_with_token():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            allFoldpulsarsummarys {
                totalObservations
                totalPulsars
                totalObservationTime
                totalProjectTime
                edges {
                    node {
                        pulsar {name}
                        latestObservation
                        firstObservation
                        mostCommonProject
                        timespan
                        numberOfObservations
                        totalIntegrationHours
                        avgSnPipe
                        highestSn
                        lastSn
                        lastIntegrationMinutes
                    }
                }
            }
        }
    """
    )
    expected = {
        'allFoldpulsarsummarys': {
            'totalObservations': 2,
            'totalPulsars': 1,
            'totalObservationTime': 0,
            'totalProjectTime': 0,
            'edges': [
                {
                    'node': {
                        'pulsar': {'name': 'J0125-2327'},
                        'latestObservation': '2019-05-14T10:14:18+00:00',
                        'firstObservation': '2019-04-23T06:11:30+00:00',
                        'mostCommonProject': 'RelBin',
                        'timespan': 22,
                        'numberOfObservations': 2,
                        'totalIntegrationHours': 0.36222222222222217,
                        'avgSnPipe': 66.727332977142,
                        'lastSn': 50.0,
                        'highestSn': 100.0,
                        'lastIntegrationMinutes': 17.33333333333333
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_query_with_proposal_and_band():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            allFoldpulsarsummarys {
                totalObservations
                totalObservationTime
                totalPulsars
                edges {
                    node {
                        pulsar {name}
                    }
                }
            }
        }
    """
    )
    expected = {
        "allFoldpulsarsummarys": {
            "totalObservations": 2,
            "totalObservationTime": 0,
            "totalPulsars": 1,
            "edges": [
                {
                    "node": {
                        "pulsar": {
                            "name": "J0125-2327"
                        }
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_fold_detail_query():
    client, user, jname = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            foldPulsarResult(pulsar:"J0125-2327") {
                totalObservations
                totalObservationHours
                totalProjects
                totalEstimatedDiskSpace
                totalTimespanDays
                description
                maxPlotLength
                minPlotLength
                edges {
                    node {
                        observation{
                            utcStart
                            duration
                            beam
                            bandwidth
                            nchan
                            band
                            foldNbin
                            nant
                            nantEff
                            project{
                                short
                            }
                            ephemeris {
                                dm
                            }
                        }
                        pipelineRun{
                            dm
                            rm
                            sn
                            flux
                            ephemeris {
                                ephemerisData
                            }
                        }
                    }
                }
            }
        }
        """
    )
    expected = {
        'allFoldPulsarResults': {
            'totalObservations': 2,
            'totalObservationHours': 0,
            'totalProjects': 1,
            'totalEstimatedDiskSpace': '590.9\xa0MB',
            'totalTimespanDays': 22,
            'description': None,
            'maxPlotLength': 1039,
            'minPlotLength': 263,
            'edges': [
                {
                    'node': {
                        'observation': {
                            'utcStart': '2019-04-23T06:11:30+00:00',
                            'duration': 263.99999999999994,
                            'beam': 1,
                            'bandwidth': 775.75,
                            'nchan': 928,
                            'band': 'LBAND',
                            'foldNbin': 1024,
                            'nant': 56,
                            'nantEff': 56,
                            'project': {
                                'short': 'RelBin'
                            },
                            'ephemeris': {
                                'dm': 9.593172234774427
                            }
                        },
                        'pipelineRun': {
                            'dm': 20,
                            'rm': 10.,
                            'sn': 100.0,
                            'flux': 25.,
                            'ephemeris': {
                                'ephemerisData': '"{\\"PSRJ\\": \\"J0125-2327\\", \\"RAJ\\": \\"01:25:01.0743144\\", \\"RAJ_ERR\\": \\"0.00000127994845007090\\", \\"DECJ\\": \\"-23:27:08.13506\\", \\"DECJ_ERR\\": \\"0.00001918386314202124\\", \\"F0\\": \\"272.08108426663083859\\", \\"F0_ERR\\": \\"6.4759257613763480721e-13\\", \\"F1\\": \\"-1.3634461197849394512e-15\\", \\"F1_ERR\\": \\"2.8611605694875967346e-20\\", \\"PEPOCH\\": \\"59040\\", \\"POSEPOCH\\": \\"59040\\", \\"DMEPOCH\\": \\"59000\\", \\"DM\\": \\"9.5931722347744274515\\", \\"DM_ERR\\": \\"0.00084029211436534800\\", \\"DM1\\": \\"-4.5501863624492810854e-05\\", \\"DM1_ERR\\": \\"0.00002866849975313738\\", \\"DM2\\": \\"0.00084738293147097471553\\", \\"DM2_ERR\\": \\"0.00004445334526905498\\", \\"DM3\\": \\"-0.0012503975851400911455\\", \\"DM3_ERR\\": \\"0.00005554336608194772\\", \\"PMRA\\": \\"37.122521114468717596\\", \\"PMRA_ERR\\": \\"0.01698181616844164363\\", \\"PMDEC\\": \\"10.783483810973773473\\", \\"PMDEC_ERR\\": \\"0.02076253509448265297\\", \\"PX\\": \\"0.96257663645756708093\\", \\"PX_ERR\\": \\"0.04876126384389192769\\", \\"BINARY\\": \\"ELL1\\", \\"PB\\": \\"7.2771997519319034614\\", \\"PB_ERR\\": \\"0.00000000012218737166\\", \\"A1\\": \\"4.7298059399316862402\\", \\"A1_ERR\\": \\"0.00000018566063704366\\", \\"XDOT\\": \\"-3.7245353018644334973e-14\\", \\"XDOT_ERR\\": \\"9.6118865782125333897e-16\\", \\"TASC\\": \\"57089.073682561520595\\", \\"TASC_ERR\\": \\"0.00000003747303270850\\", \\"EPS1\\": \\"6.0403911424169288956e-08\\", \\"EPS1_ERR\\": \\"0.00000001036524801089\\", \\"EPS2\\": \\"3.8238495748837071794e-07\\", \\"EPS2_ERR\\": \\"0.00000000971727142073\\", \\"START\\": \\"2019-04-23T06:13:48.323095Z\\", \\"FINISH\\": \\"2022-07-27T00:46:33.004474Z\\", \\"TRACK\\": \\"-2\\", \\"TZRMJD\\": \\"59191.764430068561374\\", \\"TZRFRQ\\": \\"1453.2657670000000962\\", \\"TZRSITE\\": \\"meerkat\\", \\"FD1\\": \\"-3.703166575894558615e-05\\", \\"FD1_ERR\\": \\"0.00000670814076275845\\", \\"FD2\\": \\"2.9633689096210766486e-05\\", \\"FD2_ERR\\": \\"0.00000468543125704137\\", \\"TRES\\": \\"0.477\\", \\"EPHVER\\": \\"5\\", \\"NE_SW\\": \\"4\\", \\"CLK\\": \\"TT(BIPM2019)\\", \\"MODE\\": \\"1\\", \\"UNITS\\": \\"TCB\\", \\"TIMEEPH\\": \\"IF99\\", \\"DILATEFREQ\\": \\"Y\\", \\"PLANET_SHAPIRO\\": \\"N\\", \\"T2CMETHOD\\": \\"IAU2000B\\", \\"CORRECT_TROPOSPHERE\\": \\"Y\\", \\"EPHEM\\": \\"DE438\\", \\"NITS\\": \\"1\\", \\"NTOA\\": \\"1233\\", \\"CHI2R\\": \\"1.2315\\", \\"JUMP\\": \\"-MJD_58575.9591_1K\\", \\"DM_SERIES\\": \\"TAYLOR\\", \\"P0\\": 0.003675374944551572, \\"P0_ERR\\": 9e-18}"'
                            }
                        }
                    }
                },
                {
                    'node': {
                        'observation': {
                            'utcStart': '2019-05-14T10:14:18+00:00',
                            'duration': 1039.9999999999998,
                            'beam': 1,
                            'bandwidth': 775.75,
                            'nchan': 928,
                            'band': 'LBAND',
                            'foldNbin': 1024,
                            'nant': 54,
                            'nantEff': 54,
                            'project': {
                                'short': 'RelBin'
                            },
                            'ephemeris': {
                                'dm': 9.593172234774427
                            }
                        },
                        'pipelineRun': {
                            'dm': 20.1,
                            'rm': 10.1,
                            'sn': 50.0,
                            'flux': 25.1,
                            'ephemeris': {
                                'ephemerisData': '"{\\"PSRJ\\": \\"J0125-2327\\", \\"RAJ\\": \\"01:25:01.0743144\\", \\"RAJ_ERR\\": \\"0.00000127994845007090\\", \\"DECJ\\": \\"-23:27:08.13506\\", \\"DECJ_ERR\\": \\"0.00001918386314202124\\", \\"F0\\": \\"272.08108426663083859\\", \\"F0_ERR\\": \\"6.4759257613763480721e-13\\", \\"F1\\": \\"-1.3634461197849394512e-15\\", \\"F1_ERR\\": \\"2.8611605694875967346e-20\\", \\"PEPOCH\\": \\"59040\\", \\"POSEPOCH\\": \\"59040\\", \\"DMEPOCH\\": \\"59000\\", \\"DM\\": \\"9.5931722347744274515\\", \\"DM_ERR\\": \\"0.00084029211436534800\\", \\"DM1\\": \\"-4.5501863624492810854e-05\\", \\"DM1_ERR\\": \\"0.00002866849975313738\\", \\"DM2\\": \\"0.00084738293147097471553\\", \\"DM2_ERR\\": \\"0.00004445334526905498\\", \\"DM3\\": \\"-0.0012503975851400911455\\", \\"DM3_ERR\\": \\"0.00005554336608194772\\", \\"PMRA\\": \\"37.122521114468717596\\", \\"PMRA_ERR\\": \\"0.01698181616844164363\\", \\"PMDEC\\": \\"10.783483810973773473\\", \\"PMDEC_ERR\\": \\"0.02076253509448265297\\", \\"PX\\": \\"0.96257663645756708093\\", \\"PX_ERR\\": \\"0.04876126384389192769\\", \\"BINARY\\": \\"ELL1\\", \\"PB\\": \\"7.2771997519319034614\\", \\"PB_ERR\\": \\"0.00000000012218737166\\", \\"A1\\": \\"4.7298059399316862402\\", \\"A1_ERR\\": \\"0.00000018566063704366\\", \\"XDOT\\": \\"-3.7245353018644334973e-14\\", \\"XDOT_ERR\\": \\"9.6118865782125333897e-16\\", \\"TASC\\": \\"57089.073682561520595\\", \\"TASC_ERR\\": \\"0.00000003747303270850\\", \\"EPS1\\": \\"6.0403911424169288956e-08\\", \\"EPS1_ERR\\": \\"0.00000001036524801089\\", \\"EPS2\\": \\"3.8238495748837071794e-07\\", \\"EPS2_ERR\\": \\"0.00000000971727142073\\", \\"START\\": \\"2019-04-23T06:13:48.323095Z\\", \\"FINISH\\": \\"2022-07-27T00:46:33.004474Z\\", \\"TRACK\\": \\"-2\\", \\"TZRMJD\\": \\"59191.764430068561374\\", \\"TZRFRQ\\": \\"1453.2657670000000962\\", \\"TZRSITE\\": \\"meerkat\\", \\"FD1\\": \\"-3.703166575894558615e-05\\", \\"FD1_ERR\\": \\"0.00000670814076275845\\", \\"FD2\\": \\"2.9633689096210766486e-05\\", \\"FD2_ERR\\": \\"0.00000468543125704137\\", \\"TRES\\": \\"0.477\\", \\"EPHVER\\": \\"5\\", \\"NE_SW\\": \\"4\\", \\"CLK\\": \\"TT(BIPM2019)\\", \\"MODE\\": \\"1\\", \\"UNITS\\": \\"TCB\\", \\"TIMEEPH\\": \\"IF99\\", \\"DILATEFREQ\\": \\"Y\\", \\"PLANET_SHAPIRO\\": \\"N\\", \\"T2CMETHOD\\": \\"IAU2000B\\", \\"CORRECT_TROPOSPHERE\\": \\"Y\\", \\"EPHEM\\": \\"DE438\\", \\"NITS\\": \\"1\\", \\"NTOA\\": \\"1233\\", \\"CHI2R\\": \\"1.2315\\", \\"JUMP\\": \\"-MJD_58575.9591_1K\\", \\"DM_SERIES\\": \\"TAYLOR\\", \\"P0\\": 0.003675374944551572, \\"P0_ERR\\": 9e-18}"'
                            }
                        }
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_searchmode_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            searchmodeObservations {
                totalObservations
                totalPulsars
                edges {
                    node {
                        jname
                        project
                        latestObservation
                        firstObservation
                        timespan
                        numberOfObservations
                    }
                }
            }
        }
        """
    )

    expected = {
        "searchmodeObservations": {
            "totalObservations": 1,
            "totalPulsars": 1,
            "edges": [
                {
                    "node": {
                        "jname": "J0125-2327",
                        "project": "RelBin",
                        "latestObservation": "2000-01-21T12:59:12+00:00",
                        "firstObservation": "2000-01-21T12:59:12+00:00",
                        "timespan": 1,
                        "numberOfObservations": 1,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_searchmode_details_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            searchmodeObservationDetails(jname: "J0125-2327") {
                totalObservations
                totalProjects
                totalTimespanDays
                edges {
                    node {
                        beam
                        dec
                        dm
                        frequency
                        length
                        nantEff
                        nbit
                        nchan
                        project
                        ra
                        tsamp
                        utc
                    }
                }
            }
        }
        """
    )
    expected = {
        "searchmodeObservationDetails": {
            "totalObservations": 1,
            "totalProjects": 1,
            "totalTimespanDays": 0,
            "edges": [
                {
                    "node": {
                        "beam": 54,
                        "dec": "-23:27",
                        "dm": 2.1,
                        "frequency": 839,
                        "length": 0.0,
                        "nantEff": None,
                        "nbit": 1,
                        "nchan": 3,
                        "project": "RelBin",
                        "ra": "1:25:",
                        "tsamp": 1.20,
                        "utc": "2000-01-21T12:59:12+00:00",
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_last_session_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    create_test_session()
    response = client.execute(
        """
        query {
            sessionDisplay {
                start
                end
                numberOfObservations
                numberOfPulsars
                sessionPulsars {
                    edges {
                        node {
                            jname
                            project
                            utc
                            frequency
                            fluxHi
                            phaseVsTimeHi
                            phaseVsFrequencyHi
                            fluxLo
                            phaseVsTimeLo
                            phaseVsFrequencyLo
                        }
                    }
                }
            }
        }
        """
    )
    expected = {
        "sessionDisplay": {
            "start": "2000-01-21T12:59:12+00:00",
            "end": "2000-01-21T12:59:12+00:00",
            "numberOfObservations": 2,
            "numberOfPulsars": 2,
            "sessionPulsars": {
                "edges": [
                    {
                        "node": {
                            "jname": "J0125-2327",
                            "project": "RelBin",
                            "utc": "2000-01-21T12:59:12+00:00",
                            "frequency": 839.0,
                            "fluxHi": None,
                            "phaseVsTimeHi": None,
                            "phaseVsFrequencyHi": None,
                            "fluxLo": None,
                            "phaseVsTimeLo": None,
                            "phaseVsFrequencyLo": None,
                        }
                    },
                    {
                        "node": {
                            "jname": None,
                            "project": "RelBin",
                            "utc": "2000-01-21T12:59:12+00:00",
                            "frequency": 839,
                            "fluxHi": None,
                            "phaseVsTimeHi": None,
                            "phaseVsFrequencyHi": None,
                            "fluxLo": None,
                            "phaseVsTimeLo": None,
                            "phaseVsFrequencyLo": None,
                        }
                    },
                ]
            },
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_list_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    session = create_test_session()
    SessionDisplay.update_or_create(session)

    response = client.execute(
        """
        query {
            sessionList {
                edges {
                    node {
                        start
                        end
                        numberOfPulsars
                        numberOfObservations
                        frequency
                        projects
                        totalIntegration
                        nDishMin
                        nDishMax
                        zapFraction
                    }
                }
            }
        }
        """
    )
    expected = {
        "sessionList": {
            "edges": [
                {
                    "node": {
                        "start": "2000-01-21T12:59:12+00:00",
                        "end": "2000-01-21T12:59:12+00:00",
                        "numberOfPulsars": 2,
                        "numberOfObservations": 2,
                        "frequency": 839.0,
                        "projects": "RelBin",
                        "totalIntegration": 8,
                        "nDishMin": None,
                        "nDishMax": None,
                        "zapFraction": 0.0,
                    }
                }
            ]
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_session_display_query():
    client, user, _ = setup_query_test()
    client.authenticate(user)
    session = create_test_session()
    SessionDisplay.update_or_create(session)

    response = client.execute(
        """
        query {
            sessionDisplay {
                start
                end
                sessionPulsars {
                    start
                    end
                    numberOfObservations
                    numberOfPulsars
                    edges {
                        node {
                            integrations
                        }
                    }
                }
            }
        }
        """
    )

    expected = {
        "sessionDisplay": {
            "start": "2000-01-21T12:59:12+00:00",
            "end": "2000-01-21T12:59:12+00:00",
            "sessionPulsars": {
                "start": "2000-01-21T12:59:12+00:00",
                "end": "2000-01-21T12:59:12+00:00",
                "numberOfObservations": 2,
                "numberOfPulsars": 2,
                "edges": [{"node": {"integrations": 4}}, {"node": {"integrations": 4}}],
            },
        }
    }

    assert not response.errors
    assert response.data == expected
