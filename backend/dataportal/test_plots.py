import pytest
from datetime import datetime, timedelta
import random

from .plots import pulsar_summary_plot


def generate_random_utcs(n=10):
    min_year = 2018
    max_year = 2020

    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    datetimes = []
    for i in range(n):
        datetimes.append(start + (end - start) * random.random())

    return datetimes


def generate_random_snrs(n=10):
    return random.sample(range(1, 10000), n)


def generate_random_integrations(n=10):
    return random.sample(range(1, 256), n)


def test_pulsar_summary_plot():
    UTCs = generate_random_utcs()
    snrs = generate_random_snrs()
    lengths = generate_random_integrations()
    bands = ["L-band"] * len(UTCs)

    js, div = pulsar_summary_plot(UTCs, snrs, lengths, bands)
    assert "</div>" in div
    assert "</script>" in js
    assert js != "<script></script>"
