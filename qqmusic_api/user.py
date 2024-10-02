"""用户相关 API"""

from typing import Literal

from .utils.credential import Credential
from .utils.network import Api
from .utils.utils import get_api

API = get_api("user")


async def get_created_songlist(musicid: int) -> list[dict]:
    """通过 musicid 获取用户创建的歌单

    Args:
        musicid: musicid

    Returns:
        歌单列表
    """
    result = await Api(**API["songlist_by_uin"]).update_params(uin=str(musicid)).result
    return result["v_playlist"]


async def get_euin(musicid: int, credential: Credential) -> str:
    """通过 musicid 获取 euin

    Args:
        musicid:    musicid
        credential: 用户凭证

    Returns:
        encrypt_uin
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
        euin:       encrypt_uin
        credential: 账号凭证
    """

    def __init__(self, euin: str, credential: Credential):
        """初始化用户类

        Args:
            euin:       encrypt_uin
            credential: 账号凭证
        """
        credential.raise_for_no_musicid()
        credential.raise_for_no_musickey()

        self.euin = euin
        self.credential = credential

    async def get_homepage(self, type: Literal[0, 1] = 1):
        """获取主页信息

        Args:
            type: 主页类型

        Returns:
            主页信息
        """
        if type:
            result = (
                await Api(**API["profile"], credential=self.credential)
                .update_params(ct=20, cv=4747474, cid=205360838, userid=self.euin)
                .result
            )
        else:
            result = await Api(**API["homepage"]).update_params(IsQueryTabDetail=1, uin=self.euin).result
        return result

    async def get_created_songlist(self) -> list[dict]:
        """获取创建的歌单

        Returns:
            歌单列表
        """
        result = await Api(**API["songlist_by_euin"]).update_params(hostuin=self.euin, sin=0, size=1000).result
        data = result["data"]["disslist"]
        data.pop(0)
        return data

    async def get_fav_songlist(self, num: int = 10, page: int = 1) -> dict:
        """获取收藏歌单

        Args:
            num:  数量
            page: 页码

        Returns:
            收藏歌单列表
        """
        return (
            await Api(**API["fav_songlist_by_euin"], credential=self.credential)
            .update_params(uin=self.euin, offset=num * (page - 1), size=num)
            .result
        )

    async def get_fav_album(self, num: int = 10, page: int = 1) -> dict:
        """获取收藏专辑

        Args:
            num:  数量
            page: 页码

        Returns:
            收藏专辑列表
        """
        return (
            await Api(**API["fav_album_by_euin"], credential=self.credential)
            .update_params(euin=self.euin, offset=num * (page - 1), size=num)
            .result
        )

    async def get_fav_mv(self, num: int = 10, page: int = 1) -> dict:
        """获取收藏 MV

        Args:
            num:  数量
            page: 页码

        Returns:
            收藏 MV 列表
        """
        result = (
            await Api(**API["fav_mv_by_euin"], credential=self.credential)
            .update_params(encuin=self.euin, pagesize=num, num=page - 1)
            .result
        )
        return {"hasmore": result["hasmore"], "total": result["total"], "list": result["mvlist"]}

    async def get_follow_user(self, num: int = 10, page: int = 1) -> dict:
        """获取关注用户

        Args:
            num:  数量
            page: 页码

        Returns:
            关注用户信息
        """
        result = (
            await Api(**API["follow_user"], credential=self.credential)
            .update_params(HostUin=self.euin, From=num * (page - 1), Size=num)
            .result
        )
        return {"total": result["Total"], "list": result["List"]}

    async def get_follow_singer(self, num: int = 10, page: int = 1) -> dict:
        """获取关注歌手

        Args:
            num:  数量
            page: 页码

        Returns:
            关注歌手信息
        """
        result = (
            await Api(**API["follow_singer"], credential=self.credential)
            .update_params(HostUin=self.euin, From=num * (page - 1), Size=num)
            .result
        )
        return {"total": result["Total"], "list": result["List"]}

    async def get_fans(self, num: int = 10, page: int = 1) -> dict:
        """获取粉丝

        Args:
            num:  数量
            page: 页码

        Returns:
            粉丝信息
        """
        result = (
            await Api(**API["fans"], credential=self.credential)
            .update_params(HostUin=self.euin, From=num * (page - 1), Size=num)
            .result
        )
        return {"total": result["Total"], "list": result["List"]}

    async def get_friend(self, num: int = 10, page: int = 1) -> dict:
        """获取好友

        Args:
            num:  数量
            page: 页码

        Returns:
            好友信息
        """
        return await Api(**API["friend"], credential=self.credential).update_params(Page=page - 1, PageSize=num).result
