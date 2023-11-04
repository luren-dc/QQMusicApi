from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List

if TYPE_CHECKING:
    from qqmusic import QQMusic

from ..utils import parse_song_info


class PlaylistApi:
    """歌单Api"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def category() -> List[Dict[str, Any]]:
        """
        歌单所有分类

        Returns:
            类别ID，基本信息
        """
        response = await PlaylistApi.parent.get_data(
            module="music.playlist.PlaylistSquare", method="GetAllTag", param={}
        )
        groups = response["v_group"]
        data = []
        for group in groups:
            data.append(
                {
                    "id": group["group_id"],
                    "name": group["group_name"],
                    "item": [
                        {"id": item["id"], "name": item["name"]}
                        for item in group["v_item"]
                    ],
                }
            )
        return data

    @staticmethod
    async def content(category_id: int, last_id: int = 0, num: int = 6) -> Dict:
        """
        分类歌单内容

        Args:
            category_id: 分类id
            last_id: 上页最后的歌单id
            num: 返回数量

        Returns:
            分类内容
        """
        if category_id == 9527:
            # 获取Ai分类歌单
            response = await PlaylistApi.parent.get_data(
                module="music.playlist.AiPlCategory",
                method="get_ai_category_content",
                param={
                    "caller": "0",
                    "category_id": 9527,
                    "size": num,
                    "last_id": str(last_id),
                    "use_page": 1 if last_id == 0 else 0,
                    "cmd": 0,
                },
            )
        else:
            response = await PlaylistApi.parent.get_data(
                module="playlist.PlayListCategoryServer",
                method="get_category_content",
                param={
                    "caller": "0",
                    "category_id": category_id,
                    "size": num,
                    "last_id": str(last_id),
                    "use_page": 1 if last_id == 0 else 0,
                    "cmd": 0,
                },
            )
        return response

    @staticmethod
    async def detail(dissid: int, **kwargs) -> Dict:
        """
        歌单详细信息

        Args:
            dissid: 歌单id
            **kwargs: musicid, musickey(可选)

        Returns:
            歌单信息，歌曲信息，歌曲标签
        """
        response = await PlaylistApi.parent.get_data(
            module="srf_diss_info.DissInfoServer",
            method="CgiGetDiss",
            param={
                "new_format": 1,
                "disstid": dissid,
                "dirid": 0,
                "tag": 1,
                "need_game_ad": 0,
                "onlysonglist": 0,
                "song_begin": 0,
                "song_num": -1,
                "userinfo": 1,
                "pic_dpi": 800,
                "orderlist": 1,
                "caller": str(PlaylistApi.parent.musicid),
            },
            need_login=True,
            **kwargs,
        )
        dirinfo = response.pop("dirinfo", {})
        dirinfo["total"] = response["songlist_size"]
        return {
            "info": dirinfo,
            "list": [parse_song_info(song) for song in response["songlist"]],
            "tag": response.pop("songtag"),
        }

    @staticmethod
    async def mid(dissid: int, **kwargs) -> List:
        """
        歌单所有歌曲mid

        Args:
            dissid: 歌单id
            **kwargs: musicid, musickey(可选)

        Returns:
            mid列表
        """
        response = await PlaylistApi.detail(dissid, **kwargs)
        return [song["info"]["mid"] for song in response["list"]]
