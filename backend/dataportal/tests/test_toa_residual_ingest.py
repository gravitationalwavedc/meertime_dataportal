import json
from base64 import b64decode

from graphene_django.utils.testing import GraphQLTestCase

from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import setup_timing_obs


class ToaResidualIngestTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    def setUp(self):
        # Set up data for the tests
        # We ignore the client from setup_timing_obs and use GraphQLTestCase's client instead
        _, self.user = setup_timing_obs()
        # Force login with GraphQLTestCase's client
        self.client.force_login(self.user)

    def test_toa_ingest(self):
        query = """
        query {{
            pulsarFoldResult(pulsar: "J0437-4715", mainProject: "MeerTIME") {{
                edges {{
                    node {{
                        observation {{
                            toas(
                                dmCorrected: false
                                nsubType: "1"
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

        response = self.query(query.format(nchan=1))
        response_json = json.loads(response.content)
        for pulsarFoldResult in response_json["data"]["pulsarFoldResult"]["edges"]:
            self.assertEqual(
                len(pulsarFoldResult["node"]["observation"]["toas"]["edges"]), 2
            )  # One from each observation

        response = self.query(query.format(nchan=16))
        response_json = json.loads(response.content)
        for pulsarFoldResult in response_json["data"]["pulsarFoldResult"]["edges"]:
            self.assertEqual(
                len(pulsarFoldResult["node"]["observation"]["toas"]["edges"]), 32
            )  # 16 from each observation

        # Make some dummy residual lines
        residual_lines = []
        residual_dict = {}
        for toa_n, toa in enumerate(
            response_json["data"]["pulsarFoldResult"]["edges"][0]["node"]["observation"]["toas"]["edges"]
        ):
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
        response = self.query(mutation, variables=variables)
        content = json.loads(response.content)

        # Check the residuals are uploaded to the right toa
        for toa in content["data"]["createResidual"]["toa"]:
            self.assertIn(toa["id"], residual_dict)
            self.assertEqual(toa["residualSec"], residual_dict[toa["id"]])
