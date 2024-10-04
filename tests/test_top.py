import pytest

from qqmusic_api.top import get_top_category

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_top_category(top):
    assert await get_top_category()


async def test_get_detail(top):
    assert await top.get_detail()


async def test_get_song(top):
    assert await top.get_song()
