import pytest

from qqmusic_api.api.songlist import Songlist

pytestmark = pytest.mark.asyncio(scope="module")

songlist = Songlist(9069454203)


async def test_get_detail():
    assert await songlist.get_detail()


async def test_get_song():
    assert await songlist.get_song()


# async def test_get_song_tag():
#     assert await songlist.get_song_tag()
