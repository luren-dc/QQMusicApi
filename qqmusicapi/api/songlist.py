from typing import Any, Dict

from ..request import Request
from .config import QQMUSIC_API


class SongList:
    @classmethod
    def get_detail(
        cls, songlist_id: int, only_song: int = 0, creator_info: int = 1
    ) -> dict[str, Any]:
        """
        获取歌单详情
        :param songlist_id: 歌单id
        :param only_song: 是否只需要歌曲
        :param creator_info: 是否需要歌单创建者信息
        :return:
        """
        data: Dict[str, Any] = {
            "comm": {
                "cv": 4747474,
                "ct": 24,
                "format": "json",
                "inCharset": "utf-8",
                "outCharset": "utf-8",
                "notice": 0,
                "platform": "yqq.json",
                "needNewCode": 0,
            },
            "req_1": {
                "module": "music.srfDissInfo.aiDissInfo",
                "method": "uniform_get_Dissinfo",
                "param": {
                    "disstid": songlist_id,
                    "userinfo": 1,
                    "tag": 1,
                    "orderlist": 1,
                    "song_begin": 0,
                    "song_num": -1,
                    "onlysonglist": 0,
                },
            },
        }
        response = Request.post(QQMUSIC_API[0], data=data)
        data = response["req_1"]["data"]
        dirinfo: Dict[str, Any] = data["dirinfo"]
        n_data = {
            "title": dirinfo["title"],
            "pic": dirinfo["picurl"],
            "desc": dirinfo["desc"],
            "tag": dirinfo["tag"],
            "create_time": dirinfo["ctime"],
            "update_time": dirinfo["mtime"],
        }
        songlist = [
            {
                "songId": song["id"],
                "songMid": song["mid"],
                "songName": song["name"],
                "singer": song["singer"],
                "album": song["album"],
                "mv": song["mv"],
                "vip_play": song["pay"]["pay_play"],
                "vip_down": song["pay"]["pay_down"],
                "file": {
                    "media_mid": song["file"]["media_mid"],
                    "size_128mp3": song["file"]["size_128mp3"],
                    "size_320mp3": song["file"]["size_320mp3"],
                    "size_flac": song["file"]["size_flac"],
                },
                "time_public": song["time_public"],
                "vs": song["vs"],
            }
            for song in data["songlist"]
        ]
        n_data["songlist"] = songlist
        if creator_info:
            n_data["creator_info"] = dirinfo["creator"]
        if only_song:
            return {"code": 200, "data": songlist}
        else:
            return {"code": 200, "data": n_data}
