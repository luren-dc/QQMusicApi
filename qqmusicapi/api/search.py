from typing import Any

import requests

from ..exceptions import NumberException, RequestException, TypeException
from ..request import Request
from ..utils import Utils
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
        cls, query: str, search_type: str, page: int = 1, num: int = 2
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
        return data
        if data["code"] != 0:
            return RequestException("Wrong request")
        data = data["req_1"]["data"]["body"][search_type]["list"]
        try:
            format_data = getattr(cls, "format_" + search_type)
            return format_data(data)
        except Exception:
            return data

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
                    "docid": data["docid"],
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
                    "time_public": data["time_public"],
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
    def format_mv(cls, data: dict) -> dict[str, Any]:
        """
        格式化 mv 搜索结果
        :param data: 格式化数据
        :return:
        """
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
                    "userName": data["title"],
                    "userPic": data["pic"],
                    "uin": data["uin"],
                    "fans_num": data["fans_num"],
                    "identify": data["identify_title"],
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
            d["singer"] = d.pop("singer_list")
            del d["albumName_hilight"]
            del d["singerTransName_hilight"]
            del d["catch_song"]
            del d["singerName_hilight"]
            n_data.append(d)
        return {"code": 200, "data": n_data}
