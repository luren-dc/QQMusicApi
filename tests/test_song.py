import pytest

from qqmusic_api.song import get_song_urls, query_by_id, query_by_mid

pytestmark = pytest.mark.asyncio(scope="package")


async def test_query_by_mid(song):
    assert await query_by_mid(["004emQMs09Z1lz"])


async def test_query_by_id(song):
    assert await query_by_id([await song.id])


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
