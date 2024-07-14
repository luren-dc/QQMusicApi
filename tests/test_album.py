import pytest

from qqmusic_api.album import Album

pytestmark = pytest.mark.asyncio(scope="module")

album = Album("000MkMni19ClKG")


async def test_get_detail():
    assert await album.get_detail()


async def test_get_song():
    assert await album.get_song()
