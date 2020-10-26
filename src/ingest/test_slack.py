import pytest
from ingest.slack import post_to_slack_if_meertime


def test_post_to_slack_if_meertime():
    # this should succeed
    proposal_meertime = "SCI-123124-MB-123"
    meertime_success = post_to_slack_if_meertime("hello", proposal_meertime)

    # these should fail
    proposal_trapum = "SCI-12345-MK-123"
    trapum_success = post_to_slack_if_meertime("hello", proposal_trapum)

    proposal_com = "COM-21345-SB-123"
    com_success = post_to_slack_if_meertime("hello", proposal_com)

    assert meertime_success
    assert not trapum_success
    assert not com_success
