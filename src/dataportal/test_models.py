import pytest
from .models import Observations, Searchmode


def test_observation_band():
    observation = Observations(frequency=1238.128383)
    assert observation.band == "L-band"


def test_searchmode_band():
    search_mode = Searchmode(frequency=843)
    assert search_mode.band == "UHF"
