from web_cache.models import FoldPulsarDetail, FoldDetailImage
from dataportal.models import Foldings, Processings


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
