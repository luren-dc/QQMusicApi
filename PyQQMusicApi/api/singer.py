from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Dict, List

if TYPE_CHECKING:
    from qqmusic import QQMusic

from ..utils import parse_song_info


class SingerApi:
    """歌手Api"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def head(mid: str) -> Dict:
        """
        歌手主页头部信息

        Args:
            mid: 歌手mid

        Returns:
            Dict: 歌手主页信息
        """
        response = await SingerApi.parent.get_data(
            module="music.UnifiedHomepage.UnifiedHomepageSrv",
            method="GetHomepageHeader",
            param={
                "SingerMid": mid,
                "IsQueryTabDetail": 1,
                "TabID": "",
                "Order": -1,
            },
        )
        return response["Info"]

    @staticmethod
    async def desc(mid: str) -> str:
        """
        歌手介绍

        Args:
            mid: 歌手mid

        Returns:
            str: 歌手信息
        """
        response = await SingerApi.parent.get_data(
            module="music.musichallSinger.SingerInfoInter",
            method="GetSingerDetail",
            param={"singer_mids": [mid], "group_singer": 1, "wiki_singer": 1},
        )
        return response["singer_list"][0]["wiki"]

    @staticmethod
    async def home(mid: str) -> Dict:
        """
        歌手主页

        Args:
            mid: 歌手mid

        Returns:
            Dict: 包含简略简介，精选歌曲，精选视频，相似艺人等
        """
        response = await SingerApi.parent.get_data(
            module="music.UnifiedHomepage.UnifiedHomepageSrv",
            method="GetHomepageHeader",
            param={
                "SingerMid": mid,
                "IsQueryTabDetail": 1,
                "TabID": "",
                "Order": -1,
            },
        )
        data = response["TabDetail"]["IntroductionTab"]["List"]
        for d in data:
            if d.get("ItemType", -1) == 3:
                songlist = d["ChoiceSongList"][0]
                songlist.update(
                    {
                        "SongList": [
                            parse_song_info(song)
                            for song in songlist.get("SongList", [])
                        ]
                    }
                )
        return data

    @staticmethod
    async def song(
        mid: str, page: int = 1, num: int = 20, order: int = 0
    ) -> List[Dict]:
        """
        歌手歌曲

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式

        Returns:
            List: 歌曲信息
        """
        data = await SingerApi.tab_detail(
            mid, "song_sing", page=page, num=num, order=order
        )

        return [parse_song_info(song) for song in data["SongTab"].get("List", [])]

    @staticmethod
    async def lyric(
        mid: str, page: int = 1, num: int = 20, order: int = 0
    ) -> List[Dict]:
        """
        歌手作词

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式

        Returns:
            List: 歌曲信息
        """
        data = await SingerApi.tab_detail(
            mid, "song_lyric", page=page, num=num, order=order
        )

        return [parse_song_info(song) for song in data["SongTab"].get("List", [])]

    @staticmethod
    async def composing(
        mid: str, page: int = 1, num: int = 20, order: int = 0
    ) -> List[Dict]:
        """
        歌手作曲

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式

        Returns:
            List: 歌曲信息
        """
        data = await SingerApi.tab_detail(
            mid, "song_composing", page=page, num=num, order=order
        )

        return [parse_song_info(song) for song in data["SongTab"].get("List", [])]

    @staticmethod
    async def producer(
        mid: str, page: int = 1, num: int = 20, order: int = 0
    ) -> List[Dict]:
        """
        歌手制作人

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式

        Returns:
            List: 歌曲信息
        """
        data = await SingerApi.tab_detail(
            mid, "producer", page=page, num=num, order=order
        )

        return [parse_song_info(song) for song in data["SongTab"].get("List", [])]

    @staticmethod
    async def arranger(
        mid: str, page: int = 1, num: int = 20, order: int = 0
    ) -> List[Dict]:
        """
        歌手编曲

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式

        Returns:
            List: 歌曲信息
        """
        data = await SingerApi.tab_detail(
            mid, "arranger", page=page, num=num, order=order
        )

        return [parse_song_info(song) for song in data["SongTab"].get("List", [])]

    @staticmethod
    async def musician(
        mid: str, page: int = 1, num: int = 20, order: int = 0
    ) -> List[Dict]:
        """
        乐手

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式

        Returns:
            List: 歌曲信息
        """
        data = await SingerApi.tab_detail(
            mid, "musician", page=page, num=num, order=order
        )
        return [parse_song_info(song) for song in data["SongTab"].get("List", [])]

    @staticmethod
    async def album(
        mid: str, page: int = 1, num: int = 20, order: int = 0, filter_type: int = 0
    ) -> Dict:
        """
        专辑

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式
            filter_type: 过滤器

        Returns:
            Dict: 专辑信息，过滤器类别
        """
        data = await SingerApi.tab_detail(
            mid, "album", page=page, num=num, order=order, filter_type=filter_type
        )
        return data["AlbumTab"]

    @staticmethod
    async def video(
        mid: str, page: int = 1, num: int = 20, order: int = 0, filter_type: int = 0
    ) -> Dict:
        """
        视频

        Args:
            mid: 歌手mid
            page: 页码
            num: 每页数量
            order: 排列方式
            filter_type: 过滤器

        Returns:
            Dict: 视频信息，过滤器类别
        """
        data = await SingerApi.tab_detail(
            mid, "video", page=page, num=num, order=order, filter_type=filter_type
        )
        return data["VideoTab"]

    @staticmethod
    async def tab_detail(mid: str, tabid: str, **kwargs) -> Dict:
        """
        tab详情

        Args:
            mid: 歌手mid
            tabid: tab栏ID
            **kwargs: 其他参数
        Returns:
            Dict: 详细信息
        """
        response = await SingerApi.parent.get_data(
            module="music.UnifiedHomepage.UnifiedHomepageSrv",
            method="GetHomepageTabDetail",
            param={
                "Uin": "",
                "SingerMid": mid,
                "TabID": tabid,
                "Order": kwargs.get("order", 0),
                "PageNum": kwargs.get("page", 1) - 1,
                "PageSize": kwargs.get("num", 20),
                "AlbumExtension": {
                    "IsNeedFilterType": 1,
                    "FilterType": kwargs.get("filter_type", 0),
                },
                "VideoExtension": {
                    "TagID": kwargs.get("filter_type", 0),
                    "IsNeedTagList": 1,
                },
            },
        )

        return response

    @staticmethod
    async def follow(id: int, op: int = 0, **kwargs) -> bool:
        """
        关注歌手

        Args:
            id: 歌手id
            op:命令 0：收藏 1：取消收藏默认为0
            **kwargs: musicid, musickey

        Returns:
            bool: 是否成功
        """
        response = await SingerApi.parent.get_data(
            module="music.concern.ConcernSystem",
            method="cgi_concern_user_v2",
            param={
                "userinfo": {
                    "usertype": 1,
                    "userid": str(id),
                },
                "opertype": op,
                "source": 137,
            },
            need_login=True,
            **kwargs,
        )
        return response["safety"]["bIfShowPrompt"]

    @staticmethod
    async def often(**kwargs) -> List[Dict]:
        """
        常听歌手

        Args:
            **kwargs: musicid, musickey

        Returns:
            List: 歌手信息
        """
        response = await SingerApi.parent.get_data(
            module="music.musichallSinger.SingerList",
            method="OftenListenSinger",
            need_login=True,
            param={},
            **kwargs,
        )
        return response["singerList"]

    @staticmethod
    async def category() -> Dict:
        """
        歌手类别

        Returns:
            Dict: 所有类别
        """
        response = await SingerApi.parent.get_data(
            module="music.musichallSinger.SingerList",
            method="GetSingerList",
            param={"area": -100, "sex": -100, "genre": -100, "hastag": 1},
        )
        return response["tags"]

    @staticmethod
    async def content(area: int = -100, sex: int = -100, genre: int = -100) -> Dict:
        """
        歌手分类详情

        Args:
            area: 区域
            sex: 性别
            genre: 风格

        Returns:
            Dict: 分类所有歌手
        """
        response = await SingerApi.parent.get_data(
            module="music.musichallSinger.SingerList",
            method="GetSingerList",
            param={
                "area": area,
                "sex": sex,
                "genre": genre,
                "hastag": 0,
            },
        )
        return response["hotlist"]
