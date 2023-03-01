import pytest
from datetime import datetime
from dataportal.models import Telescopes, Foldings, Sessions
from web_cache.models import FoldPulsar, FoldPulsarDetail, SearchmodePulsar, SearchmodePulsarDetail, FoldDetailImage, \
    SessionDisplay
from web_cache.testing_utils import create_pulsar_with_observations


def create_session():
    start = datetime.strptime("1999-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z")
    end = datetime.strptime("2002-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z")
    telescope = Telescopes.objects.create(name="telescope")
    return Sessions.objects.create(start=start, end=end, telescope=telescope)


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_pulsar_save_signal():
    jname = create_pulsar_with_observations()
    assert FoldPulsar.objects.filter(jname=jname).exists()


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_pulsar_save_signal_can_update():
    jname = create_pulsar_with_observations()
    Foldings.objects.get(folding_ephemeris__pulsar__jname=jname).save()
    assert FoldPulsar.objects.filter(jname=jname).count() == 1


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_folding_save_signal():
    jname = create_pulsar_with_observations()
    assert FoldPulsarDetail.objects.filter(fold_pulsar__jname=jname).exists()


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_searchmode_save():
    jname = create_pulsar_with_observations()
    assert SearchmodePulsar.objects.filter(jname=jname).exists()


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_filterbanking_save():
    jname = create_pulsar_with_observations()
    assert SearchmodePulsarDetail.objects.filter(searchmode_pulsar__jname=jname).exists()


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_handle_image_save_is_fired():
    jname = create_pulsar_with_observations()
    assert FoldDetailImage.objects.filter(fold_pulsar_detail__fold_pulsar__jname=jname).exists()


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_handle_session_delete():
    create_pulsar_with_observations()
    session = create_session()
    session.delete()
    assert not SessionDisplay.objects.all()

@pytest.mark.django_db
@pytest.mark.enable_signals
def test_handle_session_delete_no_cache():
    create_pulsar_with_observations()
    session = create_session()
    SessionDisplay.objects.all().delete()
    session.delete()
    assert not SessionDisplay.objects.all()