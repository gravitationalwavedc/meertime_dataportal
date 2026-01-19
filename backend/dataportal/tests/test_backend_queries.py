import json

import pytz
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from graphene_django.utils.testing import GraphQLTestCase
from graphql_relay import from_global_id

from dataportal.models import Toa
from dataportal.tests.test_base import BaseTestCaseWithTempMedia
from dataportal.tests.testing_utils import setup_query_test

User = get_user_model()


class BackendQueriesTestCase(BaseTestCaseWithTempMedia, GraphQLTestCase):
    """Test cases for backend GraphQL queries and mutations"""

    @classmethod
    def setUpTestData(cls):
        """Setup basic test environment once for all test methods."""
        # Call setup_query_test once for all tests and store results as class attributes
        # GraphQLTestCase provides self.client, so we ignore the client returned by setup_query_test
        (
            _,
            cls.user,
            cls.telescope,
            cls.project,
            cls.ephemeris,
            cls.template,
            cls.pipeline_run,
            cls.observation,
            cls.cal,
        ) = setup_query_test()

        # Add the required permission to the user
        content_type = ContentType.objects.get_for_model(Toa)
        permission = Permission.objects.get(
            content_type=content_type,
            codename="add_toa",
        )
        cls.user.user_permissions.add(permission)

    def setUp(self):
        """Setup that runs before each test method."""
        # Force login with the user from setUpTestData
        self.client.force_login(self.user)

    def _create_toa(self, variables):
        """Helper method to create a TOA and return the response content."""
        mutation = """
        mutation (
            $pipelineRunId: Int!,
            $projectShort: String!,
            $templateId: Int!,
            $ephemerisText: String!,
            $toaLines: [String]!,
            $dmCorrected: Boolean!,
            $nsubType: String!,
            $obsNpol: Int!,
            $obsNchan: Int!,
        ) {
            createToa (input: {
                pipelineRunId: $pipelineRunId,
                projectShort: $projectShort,
                templateId: $templateId,
                ephemerisText: $ephemerisText,
                toaLines: $toaLines,
                dmCorrected: $dmCorrected,
                nsubType: $nsubType,
                obsNpol: $obsNpol,
                obsNchan: $obsNchan,
            }) {
                toa {
                    id
                    pipelineRun {
                        id
                    }
                    project {
                        short
                    }
                    template {
                        id
                    }
                    snr
                }
            }
        }
        """
        response = self.query(mutation, variables=variables)
        content = json.loads(response.content)
        self.assertNotIn("errors", content, "GraphQL errors should not be present")
        self.assertIn("data", content, "Response should contain data")
        self.assertIn("createToa", content["data"], "Response should contain createToa")
        self.assertIn("toa", content["data"]["createToa"], "Response should contain toa")
        self.assertIsNotNone(content["data"]["createToa"]["toa"], "TOA should not be None")
        return content["data"]["createToa"]["toa"][0]

    def _get_default_toa_variables(self):
        """Helper method to get default TOA variables."""
        return {
            "pipelineRunId": self.pipeline_run.id,
            "projectShort": self.project.short,
            "templateId": self.template.id,
            "ephemerisText": "PSRJ           J1843-1113\nRAJ             18:43:41.2604556         1  0.00000187287019363934   \nDECJ           -11:13:31.10243           1  0.00014519434163362565   \nF0             541.80974405707247615     1  0.00000000000290014298   \nF1             -2.805396363508744563e-15 1  7.4950360079566945971e-20\nPEPOCH         59039                       \nPOSEPOCH       59039                       \nDMEPOCH        59000                       \nDM             59.960738646162671586     1  0.00020287554562091809   \nDM1            0.00020848310887718364115 1  0.00006325749285346446   \nDM2            -0.00039470924257044290713 1  0.00004787328456071190   \nPMRA           -2.0795056505383888398    1  0.01747424281961072831   \nPMDEC          -3.3966211798422028098    1  0.08595125564763021753   \nPX             0.70827167084823647645    1  0.08396861546067961590   \nSTART          58596.14157014051294        \nFINISH         60154.945539417179205       \nTZRMJD         59375.168483836273452       \nTZRFRQ         1029.053000000000111     \nTZRSITE        meerkat   \nFD1            8.9844055620473225671e-06 1  0.00000113604770702304   \nTRES           1.623        \nEPHVER         5                           \nNE_SW          0                           \nCLK            TT(BIPM2020)\nMODE 1\nUNITS          TCB\nTIMEEPH        IF99\nDILATEFREQ     Y\nPLANET_SHAPIRO Y\nT2CMETHOD      IAU2000B\nCORRECT_TROPOSPHERE  Y\nEPHEM          DE440\nNITS           1\nNTOA           2886\nCHI2R          1.4926 2874\nDM_SERIES TAYLOR\n",
            "toaLines": [
                "FORMAT 1\n",
                "J1843-1113_2025-05-28-21:22:26_zap_chopped.1ch_1p_1t.ar 1285.614000 60823.892082316142783   0.686  meerkat  -fe KAT -be MKBF -f KAT_MKBF -bw 775.8 -tobs 248 -tmplt J1843-1113.std -gof 1.17 -nbin 1024 -nch 1024 -chan 0 -rcvr KAT -snr 63.434 -length 248.000000000001 -subint 0\n",
            ],
            "dmCorrected": False,
            "nsubType": "1",
            "obsNpol": 1,
            "obsNchan": 1,
        }

    def test_create_toa(self):
        """Test creating a TOA with specific data."""
        variables = self._get_default_toa_variables()
        created_toa = self._create_toa(variables)

        # Verify the created TOA has the correct relationships
        self.assertIn("id", created_toa, "TOA should have an ID")
        self.assertIn("pipelineRun", created_toa, "TOA should have a pipelineRun")
        self.assertIn("project", created_toa, "TOA should have a project")
        self.assertIn("template", created_toa, "TOA should have a template")

        # Verify the relationships match our input
        _, decoded_pipeline_run_id = from_global_id(created_toa["pipelineRun"]["id"])
        self.assertEqual(
            str(decoded_pipeline_run_id), str(self.pipeline_run.id), "TOA should be linked to the correct pipeline run"
        )
        self.assertEqual(
            created_toa["project"]["short"], self.project.short, "TOA should be linked to the correct project"
        )
        _, decoded_template_id = from_global_id(created_toa["template"]["id"])
        self.assertEqual(
            str(decoded_template_id), str(self.template.id), "TOA should be linked to the correct template"
        )

    def test_create_duplicate_toa(self):
        """Test creating a TOA with the same parameters as test_create_toa and verify it returns the same TOA."""
        variables = self._get_default_toa_variables()

        # First run
        created_toa1 = self._create_toa(variables)

        # Second run with same parameters
        created_toa2 = self._create_toa(variables)

        # Verify that the second run returns the same TOA as the first run
        self.assertEqual(
            created_toa1["id"], created_toa2["id"], "Second run should return the same TOA as the first run"
        )

    def test_update_toa(self):
        """Test updating an existing TOA by changing some fields."""
        variables = self._get_default_toa_variables()

        # First run
        created_toa1 = self._create_toa(variables)

        # Second run with different values for non-unique fields
        variables["toaLines"] = [
            "FORMAT 1\n",
            "J1843-1113_2025-05-28-21:22:26_zap_chopped.1ch_1p_1t.ar 1285.614000 60823.892082316142783   0.686  meerkat  -fe KAT -be MKBF -f KAT_MKBF -bw 775.8 -tobs 248 -tmplt J1843-1113.std -gof 1.17 -nbin 1024 -nch 1024 -chan 0 -rcvr KAT -snr 70.0 -length 248.000000000001 -subint 0\n",
        ]
        created_toa2 = self._create_toa(variables)

        # Verify that the second run returns the same TOA as the first run
        self.assertEqual(
            created_toa1["id"], created_toa2["id"], "Second run should return the same TOA as the first run"
        )
        # Verify that the TOA was updated
        self.assertEqual(created_toa2["snr"], 70.0, "TOA should be updated with snr=70.0")

    def test_pulsar_fold_result_inf_dm_err(self):
        """Test that dmErr is set to null when it is a non-scalar value (inf, -inf, nan)."""
        query = """
        query pulsarFoldResult (
            $pulsar: String,
            $mainProject: String,
            $utcStart: String,
            $beam: Int,
            $first: Int
        ) {
            pulsarFoldResult (
                pulsar: $pulsar,
                mainProject: $mainProject,
                utcStart: $utcStart,
                beam: $beam,
                first: $first
            ) {
                edges {
                    node {
                        pipelineRun { dmErr }
                    }
                }
            }
        }
        """
        # Convert naive datetime to timezone-aware datetime
        utc_start = self.observation.utc_start.replace(tzinfo=pytz.UTC)
        variables = {
            "pulsar": self.observation.pulsar.name,
            "mainProject": self.observation.project.main_project.name,
            "utcStart": utc_start.strftime("%Y-%m-%d-%H:%M:%S"),
            "beam": self.observation.beam,
            "first": 100,
        }

        # Test all non-scalar values
        for value in [float("inf"), float("-inf"), float("nan")]:
            self.pipeline_run.dm_err = value
            self.pipeline_run.save()

            response = self.query(query, variables=variables)
            content = json.loads(response.content)

            self.assertNotIn("errors", content, f"Response should not contain errors for {value}")
            dm_err = content["data"]["pulsarFoldResult"]["edges"][0]["node"]["pipelineRun"]["dmErr"]
            self.assertIsNone(dm_err, f"dmErr should be null for {value}")
