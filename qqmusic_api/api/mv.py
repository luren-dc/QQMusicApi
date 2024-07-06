import random

from ..utils.common import get_api, random_string
from ..utils.network import Api
from .song import query_by_id

API = get_api("mv")


class MV:
    """
    MV 类
    """

    def __init__(self, vid: str):
        self.vid = vid

    def __repr__(self) -> str:
        return f"MV(vid={self.vid})"

    async def get_detail(self) -> dict:
        """
        获取 MV 详细信息

        Return:
            dict: 视频信息
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
        """
        获取 MV 相关歌曲

        Return:
            list: 歌曲基本信息
        """
        param = {
            "vidlist": [self.vid],
            "required": ["related_songs"],
        }
        song_id = (await Api(**API["detail"]).update_params(**param).result)[self.vid][
            "related_songs"
        ]
        return await query_by_id(song_id)

    async def get_url(self) -> dict:
        """
        获取 MV 播放链接

        Return:
            dict: 视频播放链接
        """
        return (await get_mv_urls([self.vid]))[self.vid]


async def get_mv_urls(vid: list[str]) -> dict:
    """
    获取 MV 播放链接

    Args:
        vid: 视频 vid 列表

    Return:
        dict: 视频播放链接
    """
    param = {
        "vids": vid,
        "request_type": 10003,
        "guid": random_string(32, "abcdef1234567890"),
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

    for vid, data in result.items():
        urls[vid] = {}
        urls[vid]["mp4"] = get_play_urls(data["mp4"])
        urls[vid]["hls"] = get_play_urls(data["hls"])

    return urls
