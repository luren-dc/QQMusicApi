import pytest

from qqmusic_api.top import Top, get_top_category

pytestmark = pytest.mark.asyncio(scope="module")


top = Top(62)


async def test_top_category():
    assert await get_top_category()


async def test_get_detail():
    assert await top.get_detail()


async def test_get_song():
    assert await top.get_song()
