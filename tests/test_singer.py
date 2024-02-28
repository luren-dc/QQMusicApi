import pytest

from pyqqmusicapi import QQMusic

api = QQMusic()

@pytest.mark.asyncio
async def test_singer_detail():
    data = await api.singer.detail("001pWERg3vFgg8")
    assert data


@pytest.mark.asyncio
async def test_singer_song():
    data = await api.singer.song("001pWERg3vFgg8")
    assert data


@pytest.mark.asyncio
async def test_singer_album():
    data = await api.singer.album("001pWERg3vFgg8")
    assert data

@pytest.mark.asyncio
async def test_singer_mv():
    data = await api.singer.mv("001pWERg3vFgg8")
    assert data

@pytest.mark.asyncio
async def test_singer_similar():
    data = await api.singer.similar("001pWERg3vFgg8")
    assert data
