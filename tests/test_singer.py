import pytest

from qqmusic_api.singer import (
    Song,
    TabType,
)

pytestmark = pytest.mark.asyncio(scope="package")


async def test_get_info(singer):
    info = await singer.get_info()
    assert info


async def test_get_fans_num(singer):
    fans_num = await singer.get_fans_num()
    assert fans_num


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
    assert all(isinstance(song, Song) for song in songs)
