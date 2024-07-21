import pytest

from qqmusic_api.search import (
    complete,
    general_search,
    hotkey,
    quick_search,
    search_by_type,
)

pytestmark = pytest.mark.asyncio(scope="package")


async def test_hotkey():
    assert await hotkey()


async def test_complete():
    assert await complete("周杰伦")


async def test_quick_search():
    assert await quick_search("周杰伦")


async def test_general_search():
    assert await general_search("周杰伦")


async def test_search_by_type():
    assert len(await search_by_type("周杰伦", num=30)) == 30
