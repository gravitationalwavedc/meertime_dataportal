import pytest
from .logic import get_band, get_meertime_filters


def test_get_band_returns_correct_value():
    assert get_band(1283.582) == "L-band"
    assert get_band(1283.58203125) == "L-band"
    assert get_band(None) == None
    assert get_band("NULL") == None
    assert get_band(1283.89550781) == "L-band"
    assert get_band(815.734375) == "UHF"
    assert get_band(544) == "544"


def test_get_meertime_filters():
    expected_on_empty_input = {"proposal__proposal__startswith": "SCI", "proposal__proposal__contains": "MB"}
    expected_on_prefix_observations = {
        "observations__proposal__proposal__startswith": "SCI",
        "observations__proposal__proposal__contains": "MB",
    }
    assert get_meertime_filters() == expected_on_empty_input
    assert get_meertime_filters(prefix="observations") == expected_on_prefix_observations
