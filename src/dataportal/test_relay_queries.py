import pytest
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from graphql.error.located_error import GraphQLLocatedError
from graphql_jwt.testcases import JSONWebTokenClient
from meertime.schema import schema
from .models import Pulsars, Observations, Utcs, Proposals


def setup_query_test():
    client = JSONWebTokenClient()
    user = get_user_model().objects.create(username='buffy')
    proposal = Proposals.objects.create(proposal="SCI_thing_MB", proposal_short="cool proposal")
    pulsar = Pulsars.objects.create(jname="J111-2222")
    utc = Utcs.objects.create(utc_ts=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"))
    Observations.objects.create(
        pulsar=pulsar, utc=utc, proposal=proposal, beam=1, frequency=300, snr_pipe=4, length=20, snr_spip=1
    )
    return client, user


@pytest.mark.django_db
def test_fold_query_no_token():
    client, _ = setup_query_test()
    response = client.execute(
        """
        query {
            foldObservations(mode:"observations") {
                edges {
                    node {
                        jname
                    }
                }
            }
        }
    """
    )
    expected_error_message = 'You do not have permission to perform this action'
    assert not response.data['foldObservations']
    assert response.errors[0].message == expected_error_message


@pytest.mark.django_db
def test_fold_query_with_token():
    client, user = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            foldObservations(mode:"observations", proposal:"All", band:"All") {
                totalObservations
                totalPulsars
                totalObservationTime
                edges {
                    node {
                        jname
                        last
                        first
                        proposalShort
                        timespan
                        nobs
                        totalTintH
                        avgSnr5min
                        maxSnr5min
                        latestSnr
                        latestTintM
                    }
                }
            }
        }
    """
    )
    expected = {
        'foldObservations': {
            'totalObservations': 1,
            'totalPulsars': 1,
            'totalObservationTime': 0,
            'edges': [
                {
                    'node': {
                        'jname': 'J111-2222',
                        'last': '2000-01-01T12:59:12+00:00',
                        'first': '2000-01-01T12:59:12+00:00',
                        'proposalShort': 'cool proposal',
                        'timespan': '0:00:00',
                        'nobs': 1,
                        'totalTintH': 0.0,
                        'avgSnr5min': 15.5,
                        'maxSnr5min': 15.5,
                        'latestSnr': 1.0,
                        'latestTintM': 0.3,
                    }
                }
            ],
        }
    }
    assert not response.errors
    assert response.data == expected


@pytest.mark.django_db
def test_fold_query_with_proposal_and_band():
    client, user = setup_query_test()
    client.authenticate(user)
    response = client.execute(
        """
        query {
            foldObservations(mode:"observations", proposal:"cool proposal", band:"UFH"){
                totalObservations
                totalObservationTime
                totalPulsars
                edges {
                    node {
                        jname
                    }
                }
            }
        }
    """
    )
    expected = {
        'foldObservations': {
            'totalObservations': 1,
            'totalObservationTime': 0,
            'totalPulsars': 1,
            'edges': [{'node': {'jname': 'J111-2222'}}],
        }
    }
    assert not response.errors
    assert response.data == expected
