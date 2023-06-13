import random
from typing import Any

from ..exceptions import ParamsException, TypeException
from ..request import Request
from ..utils import Utils
from .config import QQMUSIC_API


class Song:
    file_type = {
        "m4a": {
            "s": "C400",
            "e": ".m4a",
        },
        "128": {
            "s": "M500",
            "e": ".mp3",
        },
        "320": {
            "s": "M800",
            "e": ".mp3",
        },
        "flac": {
            "s": "F000",
            "e": ".flac",
        },
    }

    @classmethod
    def url(cls, song_mid: list[str], file_type: str = "128") -> dict[str, Any]:
        """
        获取歌曲链接
        :param song_mid: 歌曲mid
        :param file_type: 128/320/flac/m4a
        :return:
        """
        if not song_mid:
            raise ParamsException("缺少 mid")
        try:
            file_info = cls.file_type[file_type]
        except KeyError:
            raise TypeException("Wrong file type")
        mid = [song_mid[i : i + 100] for i in range(0, len(song_mid), 100)]
        urls = {}
        for m in mid:
            data = {
                "comm": {
                    "cv": 4747474,
                    "ct": 24,
                    "format": "json",
                    "inCharset": "utf-8",
                    "outCharset": "utf-8",
                    "notice": 0,
                    "platform": "yqq.json",
                    "needNewCode": 0,
                },
                "req_1": {
                    "module": "vkey.GetVkeyServer",
                    "method": "CgiGetVkey",
                    "param": {
                        "filename": [
                            f"{file_info['s']}{_}{_}{file_info['e']}" for _ in m
                        ],
                        "guid": Utils.get_guid(),
                        "songmid": m,
                        "songtype": [0 for _ in mid],
                        "uin": "0",
                        "loginflag": 1,
                        "platform": "20",
                    },
                },
            }
            response = Request.post(QQMUSIC_API[0], data=data)
            sip = random.choice(response["req_1"]["data"]["sip"])
            for data in response["req_1"]["data"]["midurlinfo"]:
                urls[data["songmid"]] = sip + data["purl"] if data["purl"] else -1
        return {"code": 200, "data": urls}
