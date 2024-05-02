import pytest

from qqmusic_api.api.search import (
    complete,
    general_search,
    hotkey,
    quick_search,
    search_by_type,
)


@pytest.mark.timeout(60)
@pytest.mark.asyncio
async def test_hotkey():
    assert await hotkey()


@pytest.mark.timeout(60)
@pytest.mark.asyncio
async def test_complete():
    assert await complete("周杰伦")


@pytest.mark.timeout(60)
@pytest.mark.asyncio
async def test_quick_search():
    assert await quick_search("周杰伦")


@pytest.mark.timeout(60)
@pytest.mark.asyncio
async def test_general_search():
    assert await general_search("周杰伦")


@pytest.mark.timeout(60)
@pytest.mark.asyncio
async def test_search_by_type():
    assert await search_by_type("周杰伦")
