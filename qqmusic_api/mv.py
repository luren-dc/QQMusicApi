"""MV 相关 API"""

import random

from .song import query_song
from .utils.common import get_api, get_guid
from .utils.network import Api

API = get_api("mv")


class MV:
    """MV 类

    Attributes:
        vid: mv id
    """

    def __init__(self, vid: str):
        """初始化 MV 类

        Args:
            vid: 视频 id
        """
        self.vid = vid

    async def get_detail(self) -> dict:
        """获取 MV 详细信息

        Returns:
            视频信息
        """
        param = {
            "vidlist": [self.vid],
            "required": [
                "vid",
                "type",
                "sid",
                "cover_pic",
                "duration",
                "singers",
                "video_switch",
                "msg",
                "name",
                "desc",
                "playcnt",
                "pubdate",
                "isfav",
                "gmid",
                "uploader_headurl",
                "uploader_nick",
                "uploader_encuin",
                "uploader_uin",
                "uploader_hasfollow",
                "uploader_follower_num",
                "uploader_hasfollow",
            ],
        }
        return (await Api(**API["detail"]).update_params(**param).result)[self.vid]

    async def get_related_song(self) -> list[dict]:
        """获取 MV 相关歌曲

        Returns:
            歌曲基本信息
        """
        param = {
            "vidlist": [self.vid],
            "required": ["related_songs"],
        }
        song_id = (await Api(**API["detail"]).update_params(**param).result)[self.vid]["related_songs"]
        return await query_song(song_id)

    async def get_url(self) -> dict:
        """获取 MV 播放链接

        Returns:
            视频播放链接
        """
        return (await get_mv_urls([self.vid]))[self.vid]


async def get_mv_urls(vid: list[str]) -> dict:
    """获取 MV 播放链接

    Args:
        vid: 视频 vid 列表

    Returns:
        视频播放链接
    """
    param = {
        "vids": vid,
        "request_type": 10003,
        "guid": get_guid(),
        "videoformat": 1,
        "format": 265,
        "dolby": 1,
        "use_new_domain": 1,
        "use_ipv6": 1,
    }
    result = await Api(**API["url"]).update_params(**param).result
    urls: dict[str, dict] = {}

    def get_play_urls(data):
        play_urls = {}
        for url_info in data:
            if url_info["freeflow_url"]:
                play_url = random.choice(url_info["freeflow_url"])
                play_urls[url_info["filetype"]] = play_url
        return play_urls

    for _, data in result.items():
        urls[_] = {}
        urls[_]["mp4"] = get_play_urls(data["mp4"])
        urls[_]["hls"] = get_play_urls(data["hls"])

    return urls
