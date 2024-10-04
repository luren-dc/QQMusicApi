import pytest

pytestmark = pytest.mark.asyncio(scope="session")


async def test_get_detail(album):
    assert await album.get_detail()


async def test_get_song(album):
    assert await album.get_song()
