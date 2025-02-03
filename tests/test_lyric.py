import pytest

from qqmusic_api.lyric import get_lyric

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_lyric():
    lyric = await get_lyric(
        "001CJxVG1yppB0",
        qrc=True,
        trans=True,
        roma=True,
    )

    assert lyric["lyric"]
    assert lyric["trans"]
    assert lyric["roma"]
