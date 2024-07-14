import pytest

from qqmusic_api.mv import MV, get_mv_urls

pytestmark = pytest.mark.asyncio(scope="module")

mv = MV("003HjRs318mRL2")


async def test_get_detail():
    await mv.get_detail()


async def test_get_related_song():
    await mv.get_related_song()


async def test_get_mv_url():
    await mv.get_url()


async def test_get_mv_urls():
    await get_mv_urls([mv.vid])
