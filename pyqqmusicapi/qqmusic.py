import json
import threading
from typing import Dict

import aiohttp

from .api import LoginApi, SearchApi, SongApi, TopApi, set_parent
from .exceptions import NotLoginedException, RequestException
from .qimei import Qimei
from .utils import random_string

_thread_lock = threading.Lock()


class QQMusic:
    """
    请求QQ音乐的核心接口，仅创建一次
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(
        self,
        musicid: str = "",
        musickey: str = "",
    ):
        """
        初始化QQ音乐核心接口

        Args:
            musicid: QQ音乐ID
            musickey: QQ音乐key
        """
        with _thread_lock:
            self._initialize(
                musicid=musicid,
                musickey=musickey,
            )

    def _initialize(self, *args, **kwargs):
        qimei = Qimei.get()
        if not qimei.q36:
            self._qimei36 = "cc8d07a748d4be0a8b91eacd100014a1730e"
        else:
            self._qimei36 = qimei.q36
        self._uid = random_string(10, "0123456789")

        self.musicid = kwargs.get("musicid", "")
        self.musickey = kwargs.get("musickey", "")

        set_parent(self)
        self.search = SearchApi
        self.login = LoginApi
        self.song = SongApi
        self.top = TopApi

    def update_token(self, musicid: str, musickey: str):
        """
        更新QQ音乐token

        Args:
            musicid: QQ音乐ID
            musickey: QQ音乐key
        """
        with _thread_lock:
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
            "QIMEI36": self._qimei36,
            "uid": self._uid,
            "format": "json",
            "inCharset": "utf-8",
            "outCharset": "utf-8",
        }

        if kwargs.get("login_method", None):
            common["tmeLoginMethod"] = str(kwargs.get("login_method", 0))

        musicid = kwargs.get("musicid", self.musicid)
        musickey = kwargs.get("musickey", self.musickey)

        if kwargs.get("need_login", False) and musicid:
            common["qq"] = str(musicid)
            common["authst"] = musickey
            if "W_X" in musickey:
                login_type = 1
            else:
                login_type = 2
        else:
            login_type = kwargs.get("login_type", 0)
        common["tmeLoginType"] = str(login_type)

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
            raise NotLoginedException("请检查QQ音乐token")
        res_data = res["request"].get("data", {})
        if not res_data:
            raise RequestException("获取接口数据失败，请检查提交的数据")
        return res_data
