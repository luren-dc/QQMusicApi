import pytest

from pyqqmusicapi import QQMusic

api = QQMusic()


@pytest.mark.asyncio
async def test_integrate():
    data = await api.search.integrate("周杰伦")
    assert data


@pytest.mark.asyncio
async def test_quick():
    data = await api.search.quick("周杰伦")
    assert data


@pytest.mark.asyncio
async def test_query():
    data = await api.search.query("周杰伦")
    assert data


@pytest.mark.asyncio
async def test_selectors():
    data = await api.search.selectors("周杰伦")
    assert data


@pytest.mark.asyncio
async def test_completion():
    data = await api.search.completion("周", True)
    assert data


@pytest.mark.asyncio
async def test_hotkey():
    hotkey = await api.search.hotkey()
    assert hotkey
