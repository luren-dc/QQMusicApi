from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List

if TYPE_CHECKING:
    from qqmusic import QQMusic


class UserApi:
    """用户Api"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def detail(uin: str, **kwargs) -> Dict[str, Any]:
        """
        用户主页

        Args:
            uin: 用户加密uin
            **kwargs: musicid, musickey

        Returns:
            包含用户信息，音乐基因，乐库，用户歌单等信息
        """
        response = await UserApi.parent.get_data(
            module="music.UnifiedHomepage.UnifiedHomepageSrv",
            method="GetHomepageHeader",
            param={
                "Uin": uin,
                "IsQueryTabDetail": 1,
                "TabID": "",
                "Order": 1,
            },
            need_login=1,
            **kwargs,
        )
        return response

    @staticmethod
    async def playlist(**kwargs) -> Dict[str, Any]:
        """
        用户歌单

        Args:
            **kwargs: musicid, musickey

        Returns:
            Dict: 歌单信息
        """
        response = await UserApi.parent.get_data(
            module="music.mobileAsset.GetFav",
            method="CgiGetSelfDiss",
            param={"getTipInfo": 1, "local_time": int(time.time())},
            need_login=1,
            **kwargs,
        )
        return response["selfDirs"]

    @staticmethod
    async def song(**kwargs) -> List[Dict]:
        """
        用户收藏歌曲

        Args:
            **kwargs: musicid, musickey

        Returns:
            歌曲信息
        """
        from .playlist import PlaylistApi

        response = await UserApi.parent.get_data(
            module="music.mobileAsset.GetFav",
            method="CgiGetSelfDiss",
            param={"getTipInfo": 1, "local_time": int(time.time())},
            need_login=1,
            **kwargs,
        )
        for diss in response["selfDirs"]:
            if diss.get("title", "") == "我喜欢":
                return (await PlaylistApi.detail(diss.get("disstid", 0), **kwargs))[
                    "list"
                ]

        return []

    @staticmethod
    async def diss(**kwargs) -> Dict[str, Any]:
        """
        用户收藏歌单

        Args:
            **kwargs: musicid, musickey

        Returns:
            歌单信息
        """
        response = await UserApi.parent.get_data(
            module="music.mobileAsset.GetFav",
            method="CgiGetOrderDiss",
            param={"getTipInfo": 1, "local_time": int(time.time())},
            need_login=1,
            **kwargs,
        )
        return response["orderDirs"]

    @staticmethod
    async def album(**kwargs) -> Dict[str, Any]:
        """
        用户收藏专辑

        Args:
            **kwargs: musicid, musickey

        Returns:
            专辑信息
        """
        response = await UserApi.parent.get_data(
            module="music.mobileAsset.GetFav",
            method="CgiGetOrderAlbum",
            param={"getTipInfo": 1, "local_time": int(time.time())},
            need_login=1,
            **kwargs,
        )
        return response["orderAlbums"]

    @staticmethod
    async def singer(uin: str, **kwargs) -> Dict[str, Any]:
        """
        用户喜欢歌手

        Args:
            uin: 用户加密uin
            **kwargs: musicid, musickey

        Returns:
            歌手信息
        """
        response = await UserApi.parent.get_data(
            module="music.concern.RelationList",
            method="GetFollowSingerList",
            param={"From": 0, "Size": 10, "HostUin": uin},
            need_login=1,
            **kwargs,
        )
        return response

    @staticmethod
    async def user(uin: str, **kwargs) -> Dict[str, Any]:
        """
        关注用户列表

        Args:
            uin: 用户加密uin
            **kwargs: musicid, musickey

        Returns:
            用户信息
        """
        response = await UserApi.parent.get_data(
            module="music.concern.RelationList",
            method="GetFollowUserList",
            param={"From": 0, "Size": 10, "HostUin": uin},
            need_login=1,
            **kwargs,
        )
        return response

    @staticmethod
    async def fans(uin: str, **kwargs) -> Dict[str, Any]:
        """
        粉丝列表

        Args:
            uin: 用户加密uin
            **kwargs: musicid, musickey

        Returns:
            粉丝信息
        """
        response = await UserApi.parent.get_data(
            module="music.concern.RelationList",
            method="GetFansList",
            param={"From": 0, "Size": 10, "HostUin": uin},
            need_login=1,
            **kwargs,
        )
        return response

    @staticmethod
    async def friend(**kwargs) -> Dict[str, Any]:
        """
        用户好友

        Args:
            uin: 用户加密uin
            **kwargs: musicid, musickey

        Returns:
            好友信息
        """
        response = await UserApi.parent.get_data(
            module="music.homepage.Friendship",
            method="GetFriendList",
            param={"Page": 0, "PageSize": 50},
            need_login=1,
            **kwargs,
        )
        return response

    @staticmethod
    async def visitor(uin: str, entrance: int = 0, **kwargs) -> Dict[str, Any]:
        """
        用户访客

        Args:
            uin: 用户加密uin
            entrance: 0: 谁看过我 2: 我看过谁 3: 被挡访客
            **kwargs: musicid, musickey

        Returns:
            访客信息
        """
        response = await UserApi.parent.get_data(
            module="music.homepage.HomepageVisitorSvr",
            method="GetVisitors",
            param={
                "encryptUin": uin,
                "pageSize": 30,
                "entrance": entrance,
                "lastPos": "",
            },
            need_login=1,
            **kwargs,
        )
        return response

    @staticmethod
    async def rename(name: str, **kwargs) -> bool:
        """
        修改昵称

        Args:
            name: 新名称
            **kwargs: musicid, musickey

        Returns:
            修改结果
        """
        response = await UserApi.parent.get_data(
            module="music.UserInfo.userInfoServer",
            method="AlterUserInfo",
            param={"mask": 1, "info": {"nick": name}},
            need_login=1,
            **kwargs,
        )
        return response["errMsg"] == "OK"

    @staticmethod
    async def follow(uin: str, op: int = 0, **kwargs) -> bool:
        """
        关注用户

        Args:
            uin: 用户加密uin
            op:命令 0：收藏 1：取消收藏
            **kwargs: musicid, musickey

        Returns:
            是否成功
        """
        response = await UserApi.parent.get_data(
            module="music.concern.ConcernSystem",
            method="cgi_concern_user_v2",
            param={
                "userinfo": {
                    "usertype": 0,
                    "userid": uin,
                },
                "opertype": op,
                "source": 137,
            },
            need_login=1,
            **kwargs,
        )
        return response["safety"]["bIfShowPrompt"]
