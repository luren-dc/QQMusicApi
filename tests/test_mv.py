import pytest

from qqmusic_api.mv import get_mv_urls

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_detail(mv):
    await mv.get_detail()


async def test_get_related_song(mv):
    await mv.get_related_song()


async def test_get_mv_url(mv):
    await mv.get_url()


async def test_get_mv_urls(mv):
    await get_mv_urls([mv.vid])
