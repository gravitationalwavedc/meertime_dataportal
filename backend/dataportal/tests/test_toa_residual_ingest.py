from base64 import b64decode

import pytest

from dataportal.tests.testing_utils import setup_timing_obs


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
                                nsubType: "min"
                                obsNchan: {nchan}
                            ) {{
                            edges {{
                                node {{
                                    id
                                    freqMhz
                                    length
                                    project {{
                                        short
                                    }}
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
    """

    response = client.execute(query.format(nchan=1))
    for pulsarFoldResult in response.data["pulsarFoldResult"]["edges"]:
        assert len(pulsarFoldResult["node"]["observation"]["toas"]["edges"]) == 2  # One from each observation

    response = client.execute(query.format(nchan=16))
    for pulsarFoldResult in response.data["pulsarFoldResult"]["edges"]:
        assert len(pulsarFoldResult["node"]["observation"]["toas"]["edges"]) == 32  # 16 from each observation

    # Make some dummy residual lines
    residual_lines = []
    residual_dict = {}
    for toa_n, toa in enumerate(response.data["pulsarFoldResult"]["edges"][0]["node"]["observation"]["toas"]["edges"]):
        decoded_id = b64decode(toa["node"]["id"]).decode("ascii").split(":")[1]
        residual_lines.append(f"{decoded_id},{toa['node']['mjd']},{toa_n},0.1,0.5")
        residual_dict[toa["node"]["id"]] = toa_n

    # Upload them
    mutation = """
        mutation (
            $residualLines: [String]!
            ) {
                createResidual (
                    input: {
                        residualLines: $residualLines
                    }
                ) {
                    toa {
                        id
                        residualSec
                    }
                }
            }
    """
    variables = {"residualLines": residual_lines}
    response = client.execute(mutation, variables)

    # Check the residuals are uploaded to the right toa
    for toa in response.data["createResidual"]["toa"]:
        assert toa["id"] in residual_dict
        assert toa["residualSec"] == residual_dict[toa["id"]]
