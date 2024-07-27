"""搜索相关 API"""

from enum import Enum
from typing import Union

from .song import Song
from .utils.network import Api
from .utils.utils import get_api, get_searchID, parse_song_info

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
        热搜词列表，k为热搜词，n为搜索量
    """
    params = {"search_id": get_searchID()}
    res = await Api(**API["hotkey"]).update_params(**params).result
    data = res.get("vec_hotkey", [])
    return [{"k": hotkey["query"], "n": hotkey["score"]} for hotkey in data]


async def complete(keyword: str, highlight: bool = False) -> list[str]:
    """搜索词补全

    Args:
        keyword:   关键词
        highlight: 是否高亮关键词. Defaluts to False

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
    data = res["items"]
    if highlight:
        return [item["hint_hilight"] for item in data]
    else:
        return [item["hint"] for item in data]


async def quick_search(keyword: str) -> dict:
    """快速搜索

    Args:
        keyword: 关键词

    Returns:
        包含专辑，歌手，歌曲的简略信息
    """
    res = await Api(**API["quick_search"]).update_params(key=keyword).result
    return res["data"]


async def general_search(keyword: str, page: int = 1, highlight: bool = False) -> dict:
    """综合搜索

    Args:
        keyword:   关键词
        page:      页码. Defaluts to 1
        highlight: 是否高亮关键词. Defaluts to False

    Returns:
        包含直接结果，歌曲，歌手，专辑，歌单，mv等.
    """
    params = {
        "search_id": get_searchID(),
        "search_type": 100,
        "query": keyword,
        "page_id": page,
        "highlight": highlight,
        "grp": 1,
    }
    res = await Api(**API["general_search"]).update_params(**params).result
    data = res["body"]
    return {
        "direct": data["direct_result"]["direct_group"],
        "song": [parse_song_info(d) for d in data["item_song"]["items"]],
        "singer": data["singer"]["items"],
        "album": data["item_album"]["items"],
        "songlist": data["item_songlist"]["items"],
        "mv": data["item_mv"]["items"],
    }


async def search_by_type(
    keyword: str,
    search_type: SearchType = SearchType.SONG,
    num: int = 10,
    page: int = 1,
    selectors: dict = {},
    highlight: bool = False,
) -> Union[list[dict], list[Song]]:
    """搜索

    Args:
        keyword:     关键词
        search_type: 搜索类型. Defaluts to SearchType.SONG
        num:         返回数量. Defaluts to 10
        page:        页码. Defaluts to 1
        selectors:   选择器. Defaluts to {}
        highlight:   是否高亮关键词. Defaluts to False

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
        "page_id": page,
        "selectors": selectors,
    }
    res = await Api(**API["desktop_search_by_type"]).update_params(**params).result
    types = {
        SearchType.SONG: "song",
        SearchType.SINGER: "singer",
        SearchType.ALBUM: "album",
        SearchType.SONGLIST: "songlist",
        SearchType.MV: "mv",
        SearchType.LYRIC: "song",
        SearchType.USER: "user",
        SearchType.AUDIO_ALBUM: "album",
        SearchType.AUDIO: "song",
    }
    data = res["body"][types[search_type]]["list"]
    if search_type in [SearchType.SONG, SearchType.LYRIC, SearchType.AUDIO]:
        return [Song.from_dict(song) for song in data]
    return data
