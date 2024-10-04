import pytest

from qqmusic_api.song import get_song_urls, get_try_url, query_song

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_query_song(song):
    assert await query_song(["004emQMs09Z1lz"])


async def test_get_info(song):
    assert await song.get_info()


async def test_get_detail(song):
    assert await song.get_detail()


async def test_get_related_mv(song):
    assert await song.get_related_mv()


async def test_get_producer(song):
    assert await song.get_producer()


async def test_get_labels(song):
    assert await song.get_labels()


async def test_get_sheet(song):
    assert await song.get_sheet()


async def test_get_related_songlist(song):
    assert await song.get_related_songlist()


async def test_get_similar_songs(song):
    assert await song.get_similar_song()


async def test_get_other_version(song):
    assert await song.get_other_version()


async def test_get_song_urls():
    assert await get_song_urls(["004emQMs09Z1lz"])
    assert await get_try_url("00041h1u3kgquE", "062sn0lg3VGZad")
