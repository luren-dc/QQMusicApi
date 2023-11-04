import pytest

from pyqqmusicapi import QQMusic

api = QQMusic()


@pytest.mark.asyncio
async def test_detail():
    data = await api.mv.detail("004R474623bb2x")
    assert data


@pytest.mark.asyncio
async def test_url():
    data = await api.mv.url(["004R474623bb2x"])
    assert data


@pytest.mark.asyncio
async def test_song():
    data = await api.mv.song("004R474623bb2x")
    assert data
