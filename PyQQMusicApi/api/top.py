from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Dict, Union

if TYPE_CHECKING:
    from qqmusic import QQMusic

from ..utils import parse_song_info


class TopApi:
    """排行榜Api"""

    parent: ClassVar[QQMusic]

    @staticmethod
    async def category() -> Dict[str, Dict[str, Union[str, int]]]:
        """
        所有排行榜

        Returns:
            排行榜信息，前三歌曲
        """
        response = await TopApi.parent.get_data(
            module="music.musicToplist.Toplist", method="GetAll", param={}
        )
        return response["group"]

    @staticmethod
    async def detail(
        topid: int,
        page: int = 1,
        num: int = 10,
        tag: bool = True,
        period: str = "",
    ):
        """
        排行榜详细信息

        Args:
            topid: 排行榜id
            page: 页数
            num: 返回数量
            tag: 是否返回排行榜标签
            period: 排行榜日期(year_subPeriod)

        Returns:
            排行榜信息
        """
        response = await TopApi.parent.get_data(
            module="music.musicToplist.Toplist",
            method="GetDetail",
            param={
                "topId": topid,
                "offset": num * (page - 1),
                "num": num,
                "withTags": tag,
                "period": period,
            },
        )

        response.pop("extInfoList", None)
        response.pop("indexInfoList", None)
        response.get("data", {}).pop("song", [])

        response["info"] = response.pop("data", {})
        response["list"] = [
            parse_song_info(song) for song in response.pop("songInfoList", [])
        ]
        response["tag"] = response.pop("songTagInfoList", [])

        return response
