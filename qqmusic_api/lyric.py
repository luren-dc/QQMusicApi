"""歌词 API"""

import re
from typing import Any

from qqmusic_api.utils.network import api_request

from .utils.common import qrc_decrypt

QRC_PATTERN = re.compile(r'<Lyric_.* LyricType=".*" LyricContent="(?P<content>.*?)"/>', re.DOTALL)


@api_request("music.musichallSong.PlayLyricInfo", "GetPlayLyricInfo")
async def get_lyric(
    value: str | int,
    qrc: bool = False,
    trans: bool = False,
    roma: bool = False,
):
    """获取歌词

    Args:
        value: 歌曲 id 或 mid
        qrc: 是否返回逐字歌词
        trans: 是否返回翻译歌词
        roma: 是否返回罗马歌词
    """
    params = {
        "crypt": 1,
        "ct": 11,
        "cv": 13020508,
        "lrc_t": 0,
        "qrc": qrc,
        "qrc_t": 0,
        "roma": roma,
        "roma_t": 0,
        "trans": trans,
        "trans_t": 0,
        "type": 1,
    }

    if isinstance(value, int):
        params["songId"] = value
    else:
        params["songMid"] = value

    def _processor(data: dict[str, Any]):
        lyric = qrc_decrypt(data["lyric"])
        trans = qrc_decrypt(data["trans"])
        roma = qrc_decrypt(data["roma"])

        if lyric and qrc:
            m_qrc = QRC_PATTERN.search(lyric)
            if m_qrc and m_qrc.group("content"):
                lyric = m_qrc.group("content")

        if roma:
            m_roma = QRC_PATTERN.search(roma)
            if m_roma and m_roma.group("content"):
                roma = m_roma.group("content")

        return {
            "lyric": lyric,
            "trans": trans,
            "roma": roma,
        }

    return params, _processor
