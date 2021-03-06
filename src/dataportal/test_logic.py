import pytest
from .logic import get_band, get_meertime_filters, get_trapum_filters, get_band_filters


def test_get_band_returns_correct_value():
    assert get_band(1283.582) == "L-band"
    assert get_band(1283.58203125) == "L-band"
    assert get_band(None) == "Unknown"
    assert get_band("NULL") == "Unknown"
    assert get_band(1283.89550781) == "L-band"
    assert get_band(815.734375) == "UHF"
    assert get_band(544) == "Unknown"
    assert get_band("My band") == "Unknown"


def test_get_meertime_filters():
    expected_on_empty_input = {"proposal__startswith": "SCI", "proposal__contains": "MB"}
    expected_on_prefix_observations__proposal = {
        "observations__proposal__proposal__startswith": "SCI",
        "observations__proposal__proposal__contains": "MB",
    }
    assert get_meertime_filters() == expected_on_empty_input
    assert get_meertime_filters(prefix="observations__proposal") == expected_on_prefix_observations__proposal


def test_get_trapum_filters():
    expected_on_empty_input = {"proposal__startswith": "SCI", "proposal__contains": "MK"}
    expected_on_prefix_observations__proposal = {
        "observations__proposal__proposal__startswith": "SCI",
        "observations__proposal__proposal__contains": "MK",
    }
    assert get_trapum_filters() == expected_on_empty_input
    assert get_trapum_filters(prefix="observations__proposal") == expected_on_prefix_observations__proposal


def test_get_band_filters():
    expected_on_empty_input = {}
    expected_on_lband = {"frequency__gte": 1085.0, "frequency__lte": 1485.0}
    expected_on_prefix_observations_lband = {"frequency__gte": 1085.0, "frequency__lte": 1485.0}
    expected_on_prefix_observations_lband = {
        "observations__frequency__gte": 1085.0,
        "observations__frequency__lte": 1485.0,
    }
    assert get_band_filters() == {}
    assert get_band_filters(band="L-band") == expected_on_lband
    assert get_band_filters(band="L-band", prefix="observations") == expected_on_prefix_observations_lband
