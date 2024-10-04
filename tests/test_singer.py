import pytest

from qqmusic_api.singer import TabType

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_info(singer):
    info = await singer.get_info()
    assert info


async def test_get_tab_detail(singer):
    tab_type = TabType.WIKI
    tab_detail = await singer.get_tab_detail(tab_type)
    assert tab_detail


async def test_get_wiki(singer):
    wiki_info = await singer.get_wiki()
    assert wiki_info


async def test_get_song(singer):
    songs = await singer.get_song()
    assert isinstance(songs, list)
