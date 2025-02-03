import pytest

from qqmusic_api import singer

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_singer_list():
    assert await singer.get_singer_list()


async def test_get_info():
    assert await singer.get_info(mid="0025NhlN2yWrP4")


async def test_get_tab_detail():
    for tab_type in singer.TabType:
        assert await singer.get_tab_detail(mid="0025NhlN2yWrP4", tab_type=tab_type)


async def test_get_desc():
    assert await singer.get_desc(mids=["0025NhlN2yWrP4"])


async def test_get_song():
    assert await singer.get_songs(mid="0025NhlN2yWrP4")
