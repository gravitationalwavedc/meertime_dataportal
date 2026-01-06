from datetime import datetime, timezone

from django.test import TestCase
from model_bakery import baker

from dataportal.storage import get_template_upload_location, get_upload_location


class StorageTestCase(TestCase):
    """Test case for storage utility functions."""

    def test_get_upload_location(self):
        """Test generation of upload location paths for pipeline images."""
        expected = "MeerKAT/SCI-20180516-MB-02/J0437-4715/2020-10-10-10:10:10/4/uploaded.dat"

        pipelineimage = baker.prepare(
            "dataportal.PipelineImage",
            image_type="uploaded.dat",
            pulsar_fold_result__observation__telescope__name="MeerKAT",
            pulsar_fold_result__observation__project__code="SCI-20180516-MB-02",
            pulsar_fold_result__observation__pulsar__name="J0437-4715",
            pulsar_fold_result__observation__beam=4,
            pulsar_fold_result__observation__utc_start=datetime.strptime(
                "2020-10-10-10:10:10", "%Y-%m-%d-%H:%M:%S"
            ).replace(tzinfo=timezone.utc),
        )

        self.assertEqual(get_upload_location(pipelineimage, "uploaded.dat"), expected)

    def test_get_template_upload_location(self):
        """Test generation of upload location paths for template files."""
        expected = "SCI-20180516-MB-02/J0023+0923/LBAND/2020-08-24-03:14:33_J0023+0923.par"

        pipelinefile = baker.prepare(
            "dataportal.Template",
            pulsar__name="J0023+0923",
            project__code="SCI-20180516-MB-02",
            band="LBAND",
            created_at=datetime.strptime("2020-08-24-03:14:33", "%Y-%m-%d-%H:%M:%S").replace(tzinfo=timezone.utc),
        )

        self.assertEqual(get_template_upload_location(pipelinefile, "J0023+0923.par"), expected)
