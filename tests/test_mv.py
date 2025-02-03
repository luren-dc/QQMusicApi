import pytest

from qqmusic_api import mv

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_detail():
    assert await mv.get_detail(["003HjRs318mRL2"])


async def test_get_mv_urls():
    await mv.get_mv_urls(["003HjRs318mRL2"])
