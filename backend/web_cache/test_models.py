from web_cache.models import FoldPulsarDetail


def test_estimated_size():
    fold_pulsar_detail = FoldPulsarDetail(length=5, tsubint=2, nbin=2, nchan=4, npol=2)
    assert fold_pulsar_detail.estimated_size == 96


def test_estimated_size_with_bad_data():
    fold_pulsar_detail = FoldPulsarDetail(length=1, tsubint=0)
    assert fold_pulsar_detail.estimated_size == 0
