from typing import Any

from ..utils import Utils


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
            return {"code": 500, "msg": "Wrong search type"}
        if page < 0:
            return {"code": 500, "msg": "Wrong page"}
        if num < 0:
            return {"code": 500, "msg": "Wrong page number"}
