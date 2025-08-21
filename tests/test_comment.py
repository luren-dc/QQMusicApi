import pytest

from qqmusic_api.comment import get_comment_count, get_hot_comments

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_comment():
    comment = await get_hot_comments(
        "542574330",
        1,
        10,
    )

    assert comment[0]["Content"]


async def test_get_comment_count():
    assert await get_comment_count("103540151")
