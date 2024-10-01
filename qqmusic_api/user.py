"""用户相关 API"""

from typing import Optional

from .utils.credential import Credential
from .utils.network import Api
from .utils.utils import get_api

API = get_api("user")


async def get_login_user_info(credential: Credential) -> dict:
    """获取登录用户信息

    Args:
        credential: 用户凭证

    Returns:
        用户信息
    """
    return (await Api(**API["login_user_info"], credential=credential).result)["info"]


async def get_euin(musicid: int, credential: Credential) -> str:
    """通过 musicid 获取 euin

    Args:
        musicid:    QQ音乐 musicid
        credential: 用户凭证

    Returns:
        QQ音乐 encrypt_uin
    """
    result = (
        await Api(**API["profile"], credential=credential)
        .update_params(ct=20, cv=4747474, cid=205360838, userid=musicid)
        .result
    )
    if result["code"] != 0:
        return ""
    return result["data"]["creator"]["encrypt_uin"]


class User:
    """用户类

    Attributes:
        musicid:    QQ音乐 musicid
        euin:       QQ音乐 encrypt_uin
        credential: 账号凭证
    """

    def __init__(self, *, musicid: Optional[int], euin: Optional[str], credential: Credential):
        """初始化用户类

        Args:
            musicid:    QQ音乐 musicid
            euin:       QQ音乐 encrypt_uin
            credential: 账号凭证
        """
        credential.raise_for_no_musicid()
        credential.raise_for_no_musickey()
        self.musicid = musicid or credential.musicid
        self.euin = euin or credential.encrypt_uin
        self.credential = credential

    async def get_created_songlist(self) -> list[dict]:
        """获取创建的歌单

        Returns:
            歌单列表
        """
        result = await Api(**API["songlist_by_uin"]).update_params(uin=str(self.musicid)).result
        return result["v_playlist"]

    async def get_fav_songlist(self, num: int = 10, page: int = 1):
        """获取收藏歌单

        Returns:
            收藏歌单列表
        """
        return (
            await Api(**API["fav_songlist_by_euin"], credential=self.credential)
            .update_params(uin=self.euin, offset=num * (page - 1), size=num)
            .result
        )

    async def get_fav_album(self, num: int = 10, page: int = 1):
        """获取收藏专辑

        Returns:
            收藏专辑列表
        """
        return (
            await Api(**API["fav_album_by_euin"], credential=self.credential)
            .update_params(euin=self.euin, offset=num * (page - 1), size=num)
            .result
        )

    async def get_fav_mv(self, num: int = 10, page: int = 1):
        """获取收藏 MV

        Returns:
            收藏 MV 列表
        """
        return (
            await Api(**API["fav_mv_by_euin"], credential=self.credential)
            .update_params(encuin=self.euin, pagesize=num, num=page - 1)
            .result
        )
