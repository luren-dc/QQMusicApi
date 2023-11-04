from pyqqmusicapi.qimei import Qimei


def test_get_qimei():
    qimei = Qimei.get()
    assert qimei.q36
