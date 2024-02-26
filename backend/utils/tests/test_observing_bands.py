from utils.observing_bands import get_band


def test_get_band():
    tests = [
        # freq, bw, expected_band
        (815.93359375, 544.0, "UHF"),
    ]
    for freq, bw, expected_band in tests:
        band = get_band(freq, bw)
        print(f"For freq={freq} and bw={bw}, band={band}")
        assert band == expected_band
