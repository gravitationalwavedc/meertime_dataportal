import pytest
from .logic import get_band


def test_get_band_returns_correct_value():
    assert get_band(1283.582) == "L-band"
    assert get_band(1283.58203125) == "L-band"
    assert get_band(None) == None
    assert get_band('NULL') == None
    assert get_band(1283.89550781) == "L-band"
    assert get_band(815.734375) == "UHF"
    assert get_band(544) == "544"
