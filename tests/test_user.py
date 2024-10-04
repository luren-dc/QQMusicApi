import pytest

from qqmusic_api.user import get_created_songlist, get_euin, get_musicid, get_vip_info

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_euin(credential):
    assert await get_euin(credential.musicid)


async def test_get_musicid(credential):
    assert await get_musicid(credential.encrypt_uin)


async def test_get_vip_info(credential):
    assert await get_vip_info(credential)


async def test_get_created_songlist(credential):
    assert await get_created_songlist(credential.musicid)


async def test_get_homepage(user):
    assert await user.get_homepage()


async def test_get_fav_song(user):
    assert await user.get_fav_song()


async def test_get_fav_songlist(user):
    assert await user.get_fav_songlist()


async def test_get_fav_mv(user):
    assert await user.get_fav_mv()


async def test_get_fav_album(user):
    assert await user.get_fav_album()


async def test_get_follow_user(user):
    assert await user.get_follow_user()


async def test_get_follow_singer(user):
    assert await user.get_follow_singer()


async def test_user_get_created_songlist(user):
    assert await user.get_created_songlist()


async def test_get_friend(user):
    assert await user.get_friend()


async def test_get_fans(user):
    assert await user.get_fans()


async def test_get_gene(user):
    assert await user.get_gene()
