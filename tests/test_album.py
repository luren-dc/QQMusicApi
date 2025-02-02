import pytest

from qqmusic_api import album

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_detail():
    assert await album.get_detail("000MkMni19ClKG")


async def test_get_song():
    assert len(await album.get_song("000MkMni19ClKG"))
