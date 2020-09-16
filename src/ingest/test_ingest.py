import pytest
from ingest.ingest_methods import parse_input
from dataportal.models import Observations, Searchmode, Utcs, Pulsars, Proposals, Ephemerides


@pytest.mark.django_db
def test_parse_input():
    input_fn = "ingest/example.input"
    with open(input_fn, "r") as input_fh:
        for line in input_fh:
            parse_input(line)
    assert Ephemerides.objects.all().count() == 1
    assert Observations.objects.all().count() == 6
    assert Searchmode.objects.all().count() == 1
    assert Utcs.objects.all().count() == 5
    assert Pulsars.objects.all().count() == 2
    assert Proposals.objects.all().count() == 2
