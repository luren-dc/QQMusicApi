from typing import Any

import requests

from .config import QQMUSIC_API
from ..exceptions import NumberException, TypeException
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
                "format": "json",
                "inCharset": "utf-8",
                "outCharset": "utf-8",
                "notice": 0,
                "platform": "yqq.json",
                "needNewCode": 1,
            },
            "req": {
                "module": "music.search.SearchCgiService",
                "method": "DoSearchForQQMusicLite",
                "param": {
                    "query": query,
                    "search_type": s_type,
                    "num_per_page": num,
                    "page_num": page,
                    "nqc_flag": 0,
                    "grp": 1,
                },
            },
        }
        return Request.post(QQMUSIC_API[0], data=data)
