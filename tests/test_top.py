import pytest

from qqmusic_api import top

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_top_category():
    assert await top.get_top_category()


async def test_get_detail():
    assert await top.get_detail(62)
