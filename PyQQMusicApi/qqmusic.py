import json
import threading
from typing import Dict

import aiohttp

from .exceptions import NotLoginedException, RequestException

_thread_lock = threading.Lock()


class QQMusic:
    _qimei36: str
    _uid: str

    def __init__(
        self,
        musicid: int = 0,
        musickey: str = "",
    ):
        self.musicid = musicid
        self.musickey = musickey

    async def get(self, *args, **kwargs) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            return await session.get(*args, **kwargs)

    async def post(self, *args, **kwargs) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            return await session.post(*args, **kwargs)

    async def get_data(self, module: str, method: str, param: Dict, **kwargs) -> Dict:
        # 构造公用参数
        common = {
            "ct": "11",
            "cv": "12060012",
            "v": "12060012",
            "tmeAppID": "qqmusic",
            "QIMEI36": QQMusic._qimei36,
            "uid": QQMusic._uid,
            "format": "json",
            "inCharset": "utf-8",
            "outCharset": "utf-8",
        }

        if kwargs.get("tmeLoginMethod", None):
            common["tmeLoginMethod"] = str(kwargs.get("tmeLoginMethod", 0))

        musicid = kwargs.get("musicid", self.musicid)
        musickey = kwargs.get("musickey", self.musickey)

        if kwargs.get("need_login", False) and musicid:
            common["qq"] = str(musicid)
            common["authst"] = musickey
            if "W_X" in musickey:
                tmeLoginType = 1
            else:
                tmeLoginType = 2
        else:
            tmeLoginType = kwargs.get("tmeLoginType", 0)
        common["tmeLoginType"] = str(tmeLoginType)

        # 构造请求参数
        data = {
            "comm": common,
            "request": {
                "module": module,
                "method": method,
                "param": param,
            },
        }

        # print(json.dumps(data))

        # 格式化请求数据
        formated_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        # 请求API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://u.y.qq.com/cgi-bin/musicu.fcg",
                data=formated_data.encode("utf-8"),
            ) as response:
                res = json.loads(await response.text(kwargs.get("charset", "utf-8")))

        # 返回请求数据
        code = res["request"].get("code", 0)
        if code == 1000:
            raise NotLoginedException("QQ music token is invalid.")
        res_data = res["request"].get("data", {})
        if not res_data:
            raise RequestException("获取接口数据失败，请检查提交的数据")
        return res_data
