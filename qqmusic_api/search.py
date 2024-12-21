"""搜索相关 API"""

from enum import Enum

from .utils.common import get_api, get_searchID
from .utils.network import Api

API = get_api("search")


class SearchType(Enum):
    """搜索类型

    + SONG:       歌曲
    + SINGER:     歌手
    + ALBUM:      专辑
    + SONGLIST:   歌单
    + MV:         MV
    + LYRIC:      歌词
    + USER:       用户
    + AUDIO_SONG: 节目专辑
    + AUDIO:      节目
    """

    SONG = 0
    SINGER = 1
    ALBUM = 2
    SONGLIST = 3
    MV = 4
    LYRIC = 7
    USER = 8
    AUDIO_ALBUM = 15
    AUDIO = 18


async def hotkey() -> list[dict]:
    """获取热搜词

    Returns:
        热搜词列表
    """
    params = {"search_id": get_searchID()}
    res = await Api(**API["hotkey"]).update_params(**params).result
    return res["vec_hotkey"]


async def complete(keyword: str) -> list[str]:
    """搜索词补全

    Args:
        keyword: 关键词

    Returns:
        补全结果
    """
    params = {
        "search_id": get_searchID(),
        "query": keyword,
        "num_per_page": 0,
        "page_idx": 0,
    }
    res = await Api(**API["complete"]).update_params(**params).result
    return res["items"]


async def quick_search(keyword: str) -> dict:
    """快速搜索

    Args:
        keyword: 关键词

    Returns:
        包含专辑,歌手,歌曲的简略信息
    """
    return await Api(**API["quick_search"]).update_params(key=keyword).result


async def general_search(
    keyword: str,
    page: int = 1,
    highlight: bool = True,
) -> dict:
    """综合搜索

    Args:
        keyword:   关键词
        page:      页码
        highlight: 是否高亮关键词

    Returns:
        包含直接结果,歌曲,歌手,专辑,歌单,mv等.
    """
    params = {
        "searchid": get_searchID(),
        "search_type": 100,
        "page_num": 15,
        "query": keyword,
        "page_id": page,
        "highlight": highlight,
        "grp": True,
    }
    return (await Api(**API["general_search"]).update_params(**params).result)["body"]


async def search_by_type(
    keyword: str,
    search_type: SearchType = SearchType.SONG,
    num: int = 10,
    page: int = 1,
    highlight: bool = True,
) -> list[dict]:
    """搜索

    Args:
        keyword:     关键词
        search_type: 搜索类型
        num:         返回数量
        page:        页码
        highlight:   是否高亮关键词

    Returns:
        搜索结果
    """
    params = {
        "searchid": get_searchID(),
        "query": keyword,
        "search_type": search_type.value,
        "num_per_page": num,
        "page_num": page,
        "highlight": highlight,
        "grp": True,
    }
    res = await Api(**API["mobile_search_by_type"]).update_params(**params).result
    types = {
        SearchType.SONG: "item_song",
        SearchType.SINGER: "singer",
        SearchType.ALBUM: "item_album",
        SearchType.SONGLIST: "item_songlist",
        SearchType.MV: "item_mv",
        SearchType.LYRIC: "item_song",
        SearchType.USER: "item_user",
        SearchType.AUDIO_ALBUM: "item_audio",
        SearchType.AUDIO: "item_song",
    }
    return res["body"][types[search_type]]
