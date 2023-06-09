from typing import Any, Dict, List

from ..exceptions import (
    NumberException,
    ParamsException,
    RequestException,
    TypeException,
)
from ..request import Request
from .config import QQMUSIC_API


class Search:
    SEARCH_TYPE = {
        "song": 0,
        "singer": 1,
        "album": 2,
        "mv": 4,
        "songlist": 3,
        "user": 8,
        "lyric": 7,
    }

    @classmethod
    def search(
        cls, query: str, search_type: str, page: int = 1, num: int = 10
    ) -> Dict[str, Any]:
        """
        搜索
        :param query: 搜索的关键词
        :param search_type: 搜索的类型
        :param page: 页数
        :param num: 每页数量
        :return: 搜索的结果
        """
        s_type = cls.SEARCH_TYPE.get(search_type, -1)
        if not query:
            raise ParamsException("无搜索关键词")
        if s_type == -1:
            raise TypeException("错误的搜索类型")
        if num < 0 or page < 0:
            raise NumberException("错误的页数或每页数量")
        data = {
            "comm": {
                "ct": 11,
                "cv": "1003006",
                "v": "1003006",
                "format": "json",
                "inCharset": "utf-8",
                "outCharset": "utf-8",
                "notice": 0,
                "platform": "yqq.json",
                "needNewCode": 0,
            },
            "req_1": {
                "method": "DoSearchForQQMusicDesktop",
                "module": "music.search.SearchCgiService",
                "param": {
                    "query": query,
                    "page_num": page,
                    "num_per_page": num,
                    "search_type": s_type,
                },
            },
        }

        response = Request.post(QQMUSIC_API[0], data=data)
        if response["code"] != 0:
            raise RequestException("服务器处理错误")
        index = search_type if search_type != "lyric" else "song"
        raw_data = response["req_1"]["data"]["body"][index]["list"]
        format_data = getattr(cls, f"format_{search_type}")

        return format_data(raw_data)

    @classmethod
    def quick_search(cls, query: str) -> Dict[str, Any]:
        if not query:
            raise ParamsException("无搜索关键词")
        response = Request.get(
            f"https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg?key={query}"
        )
        return {"code": 0, "data": response["data"]}

    @classmethod
    def format_song(cls, data: Dict) -> list[Dict]:
        return cls._extract_song_data(data)

    @classmethod
    def format_lyric(cls, data: Dict) -> List[Dict]:
        formatted_data = cls._extract_song_data(data)
        for index, song in enumerate(formatted_data):
            song["lyric"] = data[index]["content"]
        return formatted_data

    @staticmethod
    def _extract_song_data(data: Dict) -> List[Dict]:
        return [
            {
                "songId": d["id"],
                "songMid": d["mid"],
                "songName": d["name"],
                "docid": d["docid"],
                "tag": d["tag"],
                "singer": d["singer"],
                "album": d["album"],
                "mv": d["mv"],
                "vip_play": d["pay"]["pay_play"],
                "vip_down": d["pay"]["pay_down"],
                "file": {
                    "media_mid": d["file"]["media_mid"],
                    "size_128mp3": d["file"]["size_128mp3"],
                    "size_320mp3": d["file"]["size_320mp3"],
                    "size_flac": d["file"]["size_flac"],
                },
                "time_public": d["time_public"],
                "vs": d["vs"],
            }
            for d in data
        ]

    @classmethod
    def format_singer(cls, data: Dict) -> Dict[str, Any]:
        return data

    @classmethod
    def format_songlist(cls, data: Dict) -> Dict[str, Any]:
        return data

    @classmethod
    def format_mv(cls, data: Dict) -> List[Dict]:
        formatted_data = []
        for d in data:
            d["mvName"] = d.pop("mv_name")
            d["mvId"] = d.pop("mv_id")
            d["singer"] = d.pop("singer_list")
            d["mvPic"] = d.pop("mv_pic_url")

            del d["singerName_hilight"]
            del d["singerMID"]
            del d["mvName_hilight"]
            del d["singerid"]
            del d["singer_name"]
            del d["notplay"]
            del d["singertype"]
            del d["msg"]

            formatted_data.append(d)

        return formatted_data

    @classmethod
    def format_user(cls, data: Dict) -> List[Dict]:
        formatted_data = [
            {
                "docid": d["docid"],
                "encrypt_uin": d["encrypt_uin"],
                "userName": d["title"],
                "userPic": d["pic"],
                "uin": d["uin"],
                "fans_num": d["fans_num"],
                "identify": d["identify_title"],
            }
            for d in data
        ]
        return formatted_data

    @classmethod
    def format_album(cls, data: Dict) -> List[Dict]:
        formatted_data = []
        for d in data:
            d["singer"] = d.pop("singer_list")
            del d["albumName_hilight"]
            del d["singerTransName_hilight"]
            del d["catch_song"]
            del d["singerName_hilight"]

            formatted_data.append(d)

        return formatted_data
