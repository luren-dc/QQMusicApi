import pytest
from qqmusicapi import QQMusic


@pytest.mark.asyncio
async def test_completion():
    api = QQMusic()
    data = await api.search.completion("周", 1)
    assert data


@pytest.mark.asyncio
async def test_hotkey():
    api = QQMusic()
    hotkey = await api.search.hotkey()
    assert hotkey
