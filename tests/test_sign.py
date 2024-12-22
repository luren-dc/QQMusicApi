import pytest

from qqmusic_api.search import (
    search_by_type,
)
from qqmusic_api.utils.session import Session

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_sign():
    async with Session(enable_sign=True):
        assert len(await search_by_type("周杰伦", num=10)) == 10
