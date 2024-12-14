from qqmusic_api.utils.device import Device
from qqmusic_api.utils.qimei import get_qimei


def test_get_qimei():
    get_qimei(Device(), "13.2.5.8")
