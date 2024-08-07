from utils.observing_bands import get_band


def test_get_band():
    # Test all LBAND frequencies
    assert get_band(1283.5, 856.0) == "LBAND"
    assert get_band(1283.4409, 775.75) == "LBAND"
    assert get_band(1283.00001, 642.0) == "LBAND"
    assert get_band(1283.9999, 0) == "LBAND"

    # Test UHF min/max frequencies
    assert get_band(815.0001, 544.0) == "UHF"
    assert get_band(815.9999, 544.0) == "UHF"

    # Test SBAND min/max frequencies
    assert get_band(2185.0001, 875.0) == "SBAND_0"
    assert get_band(2188.9999, 875.0) == "SBAND_0"
    assert get_band(2404.0001, 875.0) == "SBAND_1"
    assert get_band(2407.9999, 875.0) == "SBAND_1"
    assert get_band(2623.0001, 875.0) == "SBAND_2"
    assert get_band(2626.9999, 875.0) == "SBAND_2"
    assert get_band(2841.0001, 875.0) == "SBAND_3"
    assert get_band(2844.9999, 875.0) == "SBAND_3"
    assert get_band(3060.0001, 875.0) == "SBAND_4"
    assert get_band(3063.9999, 875.0) == "SBAND_4"

    # Test Other
    assert get_band(1000, 475.2) == "OTHER"
