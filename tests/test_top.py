import pytest

from pyqqmusicapi import QQMusic

api = QQMusic()


@pytest.mark.asyncio
async def test_category():
    data = await api.top.category()
    assert data


@pytest.mark.asyncio
async def test_detail():
    data = await api.top.detail(62)
    assert data
