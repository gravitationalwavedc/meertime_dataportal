import os
import json
import copy
import pytest
from dataportal.tests.testing_utils import setup_query_test, setup_timing_obs, TEST_DATA_DIR, CYPRESS_FIXTURE_DIR
from dataportal.models import (
    Toa,
    Residual,
)


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_toa_ingest():
    client, user = setup_timing_obs()
    client.authenticate(user)
    query = """
        query {{
            pulsarFoldResult(pulsar: "J0437-4715", mainProject: "MeerTIME") {{
                edges {{
                    node {{
                        observation {{
                            toas(
                                dmCorrected: false
                                minimumNsubs: true
                                obsNchan: {nchan}
                            ) {{
                            edges {{
                                node {{
                                    freqMhz
                                    length
                                    project {{
                                        short
                                    }}
                                    residual {{
                                        mjd
                                        dayOfYear
                                        binaryOrbitalPhase
                                        residualSec
                                        residualSecErr
                                        residualPhase
                                        residualPhaseErr
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    response = client.execute(query.format(nchan=1))
    for pulsarFoldResult in response.data["pulsarFoldResult"]["edges"]:
        assert len(pulsarFoldResult["node"]["observation"]["toas"]["edges"]) == 2 # One from each observation

    response = client.execute(query.format(nchan=16))
    for pulsarFoldResult in response.data["pulsarFoldResult"]["edges"]:
        assert len(pulsarFoldResult["node"]["observation"]["toas"]["edges"]) == 32 # 16 from each observation