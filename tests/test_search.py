import pytest

from qqmusic_api.search import (
    SearchType,
    complete,
    general_search,
    hotkey,
    quick_search,
    search_by_type,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_hotkey():
    assert await hotkey()


async def test_complete():
    assert await complete("周杰伦")


async def test_quick_search():
    assert await quick_search("周杰伦")


async def test_general_search():
    assert await general_search("周杰伦")


async def test_search_by_type():
    for search_type in SearchType:
        assert len(await search_by_type("周杰伦", num=10, search_type=search_type)) == 10
