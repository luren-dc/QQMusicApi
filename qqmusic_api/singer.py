"""歌手相关 API"""

from enum import Enum
from typing import Any, Literal, cast

from .utils.network import api_request


class AreaType(Enum):
    """地区类型枚举"""

    ALL = -100
    CHINA = 200
    TAIWAN = 2
    AMERICA = 5
    EUROPE = 4
    JAPAN = 3
    KOREA = 1


class GenreType(Enum):
    """风格类型枚举"""

    ALL = -100
    POP = 7
    RAP = 3
    CHINESE_STYLE = 19
    ROCK = 4
    ELECTRONIC = 2
    FOLK = 8
    R_AND_B = 11
    ETHNIC = 37
    LIGHT_MUSIC = 93
    JAZZ = 14
    CLASSICAL = 33
    COUNTRY = 13
    BLUES = 10


class SexType(Enum):
    """性别类型枚举"""

    ALL = -100
    MALE = 0
    FEMALE = 1
    GROUP = 2


class TabType(Enum):
    """Tab 类型枚举"""

    WIKI = ("wiki", "IntroductionTab")
    ALBUM = ("album", "AlbumTab")
    COMPOSER = ("song_composing", "SongTab")
    LYRICIST = ("song_lyric", "SongTab")
    PRODUCER = ("producer", "SongTab")
    ARRANGER = ("arranger", "SongTab")
    MUSICIAN = ("musician", "SongTab")
    SONG = ("song_sing", "SongTab")
    VIDEO = ("video", "VideoTab")

    def __init__(self, tab_id: str, tab_name: str):
        self.tab_id = tab_id
        self.tab_name = tab_name


@api_request("music.musichallSinger.SingerList", "GetSingerList")
async def get_singer_list(
    area: AreaType = AreaType.ALL,
    sex: SexType = SexType.ALL,
    genre: GenreType = GenreType.ALL,
):
    """获取歌手列表

    Args:
        area: 地区
        sex: 性别
        genre: 风格
    """
    return {
        "hastag": 0,
        "area": area.value,
        "sex": sex.value,
        "genre": genre.value,
    }, lambda data: cast(
        list[dict[str, Any]],
        data["hotlist"],
    )


@api_request("music.UnifiedHomepage.UnifiedHomepageSrv", "GetHomepageHeader")
async def get_info(mid: str):
    """获取歌手基本信息

    Args:
        mid: 歌手 mid
    """
    return {"SingerMid": mid}, lambda data: data


@api_request("music.UnifiedHomepage.UnifiedHomepageSrv", "GetHomepageTabDetail")
async def get_tab_detail(mid: str, tab_type: TabType, page: int = 1, num: int = 10):
    """获取歌手 Tab 详细信息

    Args:
        mid: 歌手 mid
        tab_type: Tab 类型
        page: 页码
        num: 返回数量
    """
    params = {
        "SingerMid": mid,
        "IsQueryTabDetail": 1,
        "TabID": tab_type.tab_id,
        "PageNum": page - 1,
        "PageSize": num,
        "Order": 0,
    }

    def _processor(data: dict[str, Any]) -> list[dict[str, Any]]:
        data = data[tab_type.tab_name]
        return data.get("List", data.get("VideoList", data.get("AlbumList", data)))

    return params, _processor


@api_request("music.musichallSinger.SingerInfoInter", "GetSingerDetail")
async def get_desc(mids: list[str]):
    """获取歌手简介

    Args:
        mids: 歌手 mid 列表
    """
    return {"singer_mids": mids, "groups": 1, "wikis": 1}, lambda data: cast(list[dict[str, Any]], data["singer_list"])


async def get_songs(
    mid: str,
    tab_type: Literal[
        TabType.SONG,
        TabType.ALBUM,
        TabType.COMPOSER,
        TabType.LYRICIST,
        TabType.PRODUCER,
        TabType.ARRANGER,
        TabType.MUSICIAN,
    ] = TabType.SONG,
    page: int = 1,
    num: int = 10,
) -> list[dict[str, Any]]:
    """获取歌手歌曲

    Args:
        mid: 歌手 mid
        tab_type: Tab 类型
        page: 页码
        num:  返回数量
    """
    return await get_tab_detail(mid, tab_type, page, num)
