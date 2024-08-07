from dataclasses import dataclass


@dataclass
class Band:
    band_width: float
    low_frequency: int
    high_frequency: int

    def test_frequency_range(self, freq):
        return self.low_frequency < freq < self.high_frequency


BANDS = {
    "LBAND": Band(0, 1283, 1284),
    "UHF": Band(544.0, 815, 816),
    "SBAND_0": Band(875.0, 2185, 2189),
    "SBAND_1": Band(875.0, 2404, 2408),
    "SBAND_2": Band(875.0, 2623, 2627),
    "SBAND_3": Band(875.0, 2841, 2845),
    "SBAND_4": Band(875.0, 3060, 3064),
}


def get_band(freq, bw):
    for key, band in BANDS.items():
        if key == "LBAND" and band.test_frequency_range(freq):
            return key

        if band.band_width == bw and band.test_frequency_range(freq):
            return key

    return "OTHER"
