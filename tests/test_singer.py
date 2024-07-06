import pytest

from qqmusic_api.api.singer import (
    TabType,
    Singer,
    Song,
)

pytestmark = pytest.mark.asyncio(scope="module")

singer = Singer("0025NhlN2yWrP4")


async def test_get_info():
    info = await singer.get_info()
    assert info


async def test_get_fans_num():
    fans_num = await singer.get_fans_num()
    assert fans_num


async def test_get_tab_detail():
    tab_type = TabType.WIKI
    tab_detail = await singer.get_tab_detail(tab_type)
    assert tab_detail


async def test_get_wiki():
    wiki_info = await singer.get_wiki()
    assert wiki_info


async def test_get_song():
    songs = await singer.get_song()
    assert isinstance(songs, list)
    assert all(isinstance(song, Song) for song in songs)
