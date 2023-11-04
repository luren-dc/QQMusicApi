from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List

if TYPE_CHECKING:
    from qqmusic import QQMusic

from ..utils import random_string


class MvApi:
    """MVApi"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def detail(vid: str) -> Dict[str, Any]:
        """
        视频详细信息

        Args:
            vid: 视频id

        Returns:
            返回包含视频文件信息，名称，封面的字典。
        """
        response = await MvApi.parent.get_data(
            module="video.VideoDataServer",
            method="get_video_info_batch",
            param={
                "vidlist": [vid],
                "required": [
                    "vid",
                    "type",
                    "cover_pic",
                    "filesize",
                    "name",
                    "desc",
                    "playcnt",
                    "pubdate",
                    "singers",
                    "star_cnt",
                    "uploader_nick",
                    "uploader_headurl ",
                    "uploader_nick ",
                    "uploader_uin ",
                    "uploader_encuin ",
                    "area ",
                    "directors",
                    "language ",
                ],
            },
        )
        return response[vid]

    @staticmethod
    async def song(vid: str) -> List[Dict]:
        """
        MV相关歌曲

        Args:
            vid: 视频id

        Returns:
            包含歌曲信息的列表
        """
        response = await MvApi.parent.get_data(
            module="video.VideoDataServer",
            method="get_video_info_batch",
            param={"vidlist": [vid], "required": ["related_songs"]},
        )
        songids = response[vid]["related_songs"]
        from .song import SongApi

        return await SongApi.query_by_id(id=songids)

    @staticmethod
    async def url(vid: List[str]) -> Dict[str, Dict]:
        """
        MV播放链接

        Args:
            vid: 视频id列表

        Returns:
            包含视频类型，播放链接的字典
        """
        response = await MvApi.parent.get_data(
            module="music.stream.MvUrlProxy",
            method="GetMvUrls",
            param={
                "vids": vid,
                "request_type": 10003,
                "videoformat": 1,
                "format": 265,
                "guid": random_string(32, "abcdef1234567890"),
                "maxFiletype": 80,
                "dolby": 1,
                "testCdn": 0,
                "filetype": 30,
                "use_new_domain": 1,
                "use_ipv6": 1,
            },
        )
        return response
