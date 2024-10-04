import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_detail(songlist):
    assert await songlist.get_detail()


async def test_get_song(songlist):
    assert await songlist.get_song()


async def test_get_song_tag(songlist):
    await songlist.get_song_tag()
