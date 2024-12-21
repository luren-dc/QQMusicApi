"""歌词 API"""

import xml.etree.ElementTree as ET
from typing import Optional

from .utils.common import get_api, qrc_decrypt
from .utils.network import Api

API = get_api("lyric")


async def get_lyric(
    *,
    mid: Optional[str] = None,
    id: Optional[int] = None,
    qrc: bool = False,
    trans: bool = False,
    roma: bool = False,
) -> dict[str, str]:
    """获取歌词

    Note:
        歌曲 mid 和 id,两者至少提供一个

    Args:
        mid:   歌曲 mid
        id:    歌曲 id
        qrc:   是否返回逐字歌词
        trans: 是否返回翻译歌词
        roma:  是否返回罗马歌词

    Returns:
        {"lyric": 歌词或逐字歌词, "trans": 翻译歌词, "roma": 罗马歌词}
    """
    if mid is None and id is None:
        raise ValueError("mid or id must be provided")

    params = {
        "crypt": 1,
        "ct": 11,
        "cv": 13020508,
        "lrc_t": 0,
        "qrc": qrc,
        "qrc_t": 0,
        "roma": roma,
        "roma_t": 0,
        "songId": id,
        "songMid": mid,
        "trans": trans,
        "trans_t": 0,
        "type": 1,
    }
    res = await Api(**API["info"]).update_params(**params).result

    lyric = qrc_decrypt(res["lyric"])

    if lyric and qrc:
        try:
            root = ET.fromstring(lyric)
            lyric_info = root[1]
            lyric = lyric_info[0].attrib.get("LyricContent", lyric)
        except Exception:
            pass

    return {
        "lyric": lyric,
        "trans": qrc_decrypt(res["trans"]),
        "roma": qrc_decrypt(res["roma"]),
    }
