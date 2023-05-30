import this
from typing import Any

import requests

from .config import QQMUSIC_API
from ..exceptions import NumberException, TypeException, RequestException
from ..utils import Utils
from ..request import Request


class Search:
    SEARCH_TYPE = {
        "song": 0,
        "singer": 1,
        "album": 2,
        "mv": 4,
        "playlist": 3,
        "user": 8,
        "lyric": 7,
    }

    @classmethod
    def search(
        cls, query: str, search_type: str, page: int = 1, num: int = 10
    ) -> dict[str, Any]:
        """
        搜索
        :param query: 搜索的关键词
        :param search_type: 搜索的类型
        :param page: 页数
        :param num: 每页数量
        :return: 搜索的结果
        """
        s_type = cls.SEARCH_TYPE.get(search_type, -1)
        if s_type == -1:
            raise TypeException("Wrong search type")
        if num < 0 or page < 0:
            raise NumberException("Wrong page or number")
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
        data = Request.post(QQMUSIC_API[0], data=data)
        if data["code"] != 0:
            return RequestException("Wrong request")
        data = data["req_1"]["data"]["body"][search_type]["list"]
        format_data = getattr(cls, "format_" + search_type)
        return format_data(data)

    @classmethod
    def format_song(cls, data: dict) -> dict[str, Any]:
        """
        格式化 song 搜索结果
        :param data: 格式化数据
        :return:
        """
        n_data = []
        for data in data:
            n_data.append(
                {
                    "songId": data["id"],
                    "songMid": data["mid"],
                    "songName": data["name"],
                    "tag": data["tag"],
                    "singer": data["singer"],
                    "album": data["album"],
                    "mv": data["mv"],
                    "vip_play": data["pay"]["pay_play"],
                    "vip_down": data["pay"]["pay_down"],
                    "file": {
                        "media_mid": data["file"]["media_mid"],
                        "size_128mp3": data["file"]["size_128mp3"],
                        "size_320mp3": data["file"]["size_320mp3"],
                        "size_flac": data["file"]["size_flac"],
                    },
                    "vs": data["vs"],
                }
            )
        return {"code": 200, "data": n_data}

    @classmethod
    def format_singer(cls, data: dict) -> dict[str, Any]:
        """
        格式化 singer 搜索结果
        :param data: 格式化数据
        :return:
        """
        return {"code": 200, "data": data}

    @classmethod
    def format_user(cls, data: dict) -> dict[str, Any]:
        """
        格式化 singer 搜索结果
        :param data: 格式化数据
        :return:
        """
        n_data = []
        for data in data:
            n_data.append(
                {
                    "docid": data["docid"],
                    "encrypt_uin": data["encrypt_uin"],
                    "name": data["title"],
                    "uin": data["uin"],
                    "fans_num": data["fans_num"],
                    "identify": data["identify_title"],
                    "pic": data["pic"],
                }
            )
        return {"code": 200, "data": n_data}

    @classmethod
    def format_album(cls, data: dict) -> dict[str, Any]:
        """
        格式化 album 搜索结果
        :param data: 格式化数据
        :return:
        """
        n_data = []
        for d in data:
            n_data.append(
                {
                }
            )
        return {"code": 200, "data": data}