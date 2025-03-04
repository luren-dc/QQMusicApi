import pytest

from qqmusic_api import songlist

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_detail():
    assert await songlist.get_detail(
        9069454203,
        onlysong=False,
        tag=True,
        userinfo=True,
    )


async def test_get_songlist():
    assert await songlist.get_songlist(songlist_id=9069454203)
