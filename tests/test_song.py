import pytest

from qqmusic_api.song import Song, get_song_urls, query_by_id, query_by_mid

pytestmark = pytest.mark.asyncio(scope="module")

song = Song(mid="004emQMs09Z1lz")


async def test_query_by_mid():
    assert await query_by_mid(["004emQMs09Z1lz"])


async def test_query_by_id():
    assert await query_by_id([await song.id])


async def test_get_info():
    assert await song.get_info()


async def test_get_detail():
    assert await song.get_detail()


async def test_get_related_mv():
    assert await song.get_related_mv()


async def test_get_producer():
    assert await song.get_producer()


async def test_get_labels():
    assert await song.get_labels()


async def test_get_sheet():
    assert await song.get_sheet()


async def test_get_related_songlist():
    assert await song.get_related_songlist()


async def test_get_similar_songs():
    assert await song.get_similar_song()


async def test_get_other_version():
    assert await song.get_other_version()


async def test_get_song_urls():
    assert await get_song_urls(["004emQMs09Z1lz"])
