from typing import Any
from ..utils import Utils
from ..exceptions import TypeException
from ..request import Request


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
        "test": {
            "s": "RS02",
            "e": ".mp3",
        },
    }

    @classmethod
    def url(
        cls, song_mid: list[str], vs: list[str], file_type: str = "128"
    ) -> dict[str, Any]:
        """
        获取歌曲链接
        :param song_mid: 歌曲mid
        :param vs: 获取试听歌曲所需
        :param file_type: 128/320/flac/test
        :return:
        """
        try:
            file_info = cls.file_type[file_type]
        except KeyError:
            raise TypeException("Wrong file type")
        if file_type == "test":
            file_name = [f"{file_info['s']}{_}{file_info['e']}" for _ in vs]
            mid = [vs[i : i + 100] for i in range(0, len(vs), 100)]
        else:
            file_name = [f"{file_info['s']}{_}{_}{file_info['e']}" for _ in song_mid]
            mid = [song_mid[i : i + 100] for i in range(0, len(song_mid), 100)]
        for mid in mid:
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
                "req_0": {
                    "module": "vkey.GetVkeyServer",
                    "method": "CgiGetVkey",
                    "param": {
                        "filename": [
                            f"{file_info['s']}{_}{_}{file_info['e']}" for _ in song_mid
                        ],
                        "guid": Utils.get_guid(),
                        "songmid": ["001FrXCA2zxByt"],
                        "songtype": [0],
                        "uin": "0",
                        "loginflag": 1,
                        "platform": "20",
                    },
                },
            }
