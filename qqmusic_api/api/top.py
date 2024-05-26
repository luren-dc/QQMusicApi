from qqmusic_api.utils.network import Api
from ..utils.common import get_api, parse_song_info
import datetime

API = get_api("top")


async def get_top_category(show_detail: bool = False) -> list[dict]:
    """
    获取所有排行榜

    Args:
        show_detail: 是否显示详情(包括介绍，前三歌曲). Defaults to False

    Returns:
        list: 排行榜信息
    """
    result = await Api(**API["category"]).result
    return [
        {
            "groupId": group["groupId"],
            "groupTitle": group["groupName"],
            "topList": [
                {
                    "id": top["topId"],
                    "title": top["title"],
                    "intro": top["intro"] if show_detail else None,
                    "period": top["period"],
                    "updateTime": top["updateTime"],
                    "listenNum": top["listenNum"],
                    "picUrl": top["headPicUrl"],
                    "song": top["song"] if show_detail else None,
                }
                for top in group["toplist"]
            ],
        }
        for group in result["group"]
    ]


class Top:
    """排行榜类"""

    def __init__(self, id: int, period: str = "") -> None:
        """
        Args:
            id: 排行榜 ID
            period: 排行榜周期
        """
        self.id = id
        self.set_period(period)

    def set_period(self, period: str):
        """
        设置排行榜周期

        Args:
            year: 年
            week: 周
        """
        time_type = "%Y-%m-%d" if self.id in [4, 27, 62] else "'%Y_%W"
        self.period = period or datetime.datetime.strftime(
            datetime.datetime.now(), time_type
        )

    async def get_detail(self):
        """
        获取排行榜详细信息

        Returns:
            dict: 排行榜信息
        """
        param = {"topId": self.id, "period": self.period}
        result = await Api(**API["detail"]).update_params(**param).result
        data = result["data"]
        return {
            "id": data["topId"],
            "title": data["title"],
            "subTitle": data["titleSub"],
            "titleDetail": data["titleDetail"],
            "desc": data["intro"],
            "listenNum": data["listenNum"],
            "total": data["totalNum"],
            "updateTime": data["updateTime"],
            "period": self.period,
        }

    async def get_song(self) -> list[dict]:
        """
        获取排行榜歌曲

        Returns:
            list: 排行榜歌曲
        """
        param = {"topId": self.id, "period": self.period, "offset": 0, "num": 100}
        result = await Api(**API["detail"]).update_params(**param).result
        return [parse_song_info(song) for song in result["songInfoList"]]
