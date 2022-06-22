import pytest
from datetime import datetime
from web_cache.models import FoldPulsar, FoldPulsarDetail, FoldDetailImage
from dataportal.models import Sessions, Telescopes 

def create_fold_pulsar():
    return FoldPulsar.objects.create(
        main_project="main", 
        project="new", 
        band="L-Band", 
        jname="j1234-5678",
        latest_observation=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        first_observation=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        timespan=4,
        number_of_observations=2,
        beam="4",
        total_integration_hours=10,
        last_sn_raw=4,
        avg_sn_pipe=3,
        max_sn_pipe=2,
        last_integration_minutes=1
    )

def test_estimated_size():
    fold_pulsar_detail = FoldPulsarDetail(length=5, tsubint=2, nbin=2, nchan=4, npol=2)
    assert fold_pulsar_detail.estimated_size == 96


def test_estimated_size_with_bad_data():
    fold_pulsar_detail = FoldPulsarDetail(length=1, tsubint=0)
    assert fold_pulsar_detail.estimated_size == 0


def test_fold_detail_image_process_property():
    assert FoldDetailImage(image_type="freq.hi").process == "raw"
    assert FoldDetailImage(image_type="pta.freq.hi").process == "pta"
    assert FoldDetailImage(image_type="relbin.freq.hi").process == "relbin"


def test_fold_detail_image_resolution_property():
    assert FoldDetailImage(image_type="freq.hi").resolution == "hi"
    assert FoldDetailImage(image_type="freq.700x400").resolution == "hi"
    assert FoldDetailImage(image_type="freq.lo").resolution == "lo"
    assert FoldDetailImage(image_type="freq.500x400").resolution == "lo"


@pytest.mark.django_db
def test_get_query():
    create_fold_pulsar()
    assert FoldPulsar.get_query()
    assert FoldPulsar.get_query(band='All', project='All', main_project='All')
    assert FoldPulsar.get_query(band='l-band')
    assert not FoldPulsar.get_query(band='UHF')
    assert FoldPulsar.get_query(project='New')
    assert not FoldPulsar.get_query(project='fake')
    assert FoldPulsar.get_query(main_project='main')
    assert not FoldPulsar.get_query(main_project='fake')


def test_get_band():
    assert FoldPulsar.get_band(frequency=9999) == 'UNKNOWN'
    assert FoldPulsar.get_band(frequency=840) == 'UHF'
    assert FoldPulsar.get_band(frequency=1285) == 'L-Band'
    assert FoldPulsar.get_band(frequency=2625) == 'S-Band'

@pytest.mark.django_db
def test_get_by_session():
    create_fold_pulsar()
    start = datetime.strptime("1999-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z")
    end = datetime.strptime("2001-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z")
    assert FoldPulsar.get_by_session(session=Sessions(start=start, end=end))

@pytest.mark.django_db
def test_fold_pulsar_session_property():
   fold_pulsar = create_fold_pulsar()
   start = datetime.strptime("1999-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z")
   end = datetime.strptime("2001-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z")
   telescope = Telescopes.objects.create(name='my telescope')
   Sessions.objects.create(start=start, end=end, telescope=telescope)
   assert fold_pulsar.session

