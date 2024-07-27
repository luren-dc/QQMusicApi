"""网络请求"""

import asyncio
import atexit
import json
from dataclasses import dataclass, field
from typing import Any, Union

import aiohttp

from ..exceptions import ResponseCodeException
from .credential import Credential
from .qimei import QIMEI

QQMUSIC_VERSION = "13.2.5.8"
QQMUSIC_VERSION_CODE = 13020508
QIMEI36 = None

API_URL = "https://u.y.qq.com/cgi-bin/musicu.fcg"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
    "Referer": "https://y.qq.com",
}

__session_pool: dict[asyncio.AbstractEventLoop, aiohttp.ClientSession] = {}


def get_aiohttp_session() -> aiohttp.ClientSession:
    """获取当前模块的 aiohttp.ClientSession 对象，用于自定义请求

    Returns:
        aiohttp.ClientSession
    """
    loop = asyncio.get_event_loop()
    session = __session_pool.get(loop, None)
    if session is None:
        session = aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(), trust_env=True)
        __session_pool[loop] = session

    return session


def set_aiohttp_session(session: aiohttp.ClientSession) -> None:
    """用户手动设置 Session

    Args:
        session:  aiohttp.ClientSession 实例
    """
    loop = asyncio.get_event_loop()
    __session_pool[loop] = session


@dataclass
class Api:
    """用于请求的 Api 类

    Attributes:
        url: 请求地址. Defaults to API_URL
        method: 请求方法
        module: 请求模块. Defaults to ""
        comment: 注释. Defaults to ""
        verify: 是否验证凭据. Defaults to False
        json_body: 是否使用 json 作为载荷. Defaults to False
        data: 请求载荷. Defaults to {}
        params: 请求参数. Defaults to {}
        headers: 请求头. Defaults to {}
        credential: 凭据. Defaults to Credential()
        extra_common: 额外参数. Defaults to {}
    """

    method: str
    module: str = ""
    url: str = API_URL
    comment: str = ""
    verify: bool = False
    json_body: bool = False
    data: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    credential: Credential = field(default_factory=Credential)
    extra_common: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.module:
            self.method = self.method.upper()
        else:
            self.json_body = True
        self.original_data = self.data.copy()
        self.original_params = self.params.copy()
        self.data = {k: "" for k in self.data.keys()}
        self.params = {k: "" for k in self.params.keys()}
        self.headers = {k: "" for k in self.headers.keys()}
        self.extra_common = {k: "" for k in self.extra_common.keys()}
        self.__result: Union[dict, None] = None

    def __setattr__(self, __name: str, __value: Any) -> None:
        """每次更新参数都要把 __result 清除"""
        if self.initialized and __name != "__Api__result":
            self.__result = None
        return super().__setattr__(__name, __value)

    @property
    def initialized(self):
        """是否已经初始化"""
        return "__Api__result" in self.__dict__

    @property
    async def result(self) -> dict:
        """获取请求结果"""
        if self.__result is None:
            result = await self.request()
            if isinstance(result, dict):
                self.__result = result
                return result
        return {}

    def update_params(self, **kwargs) -> "Api":
        """毫无亮点的更新 params"""
        self.params = kwargs
        self.__result = None
        return self

    def update_data(self, **kwargs) -> "Api":
        """毫无亮点的更新 data"""
        self.data = kwargs
        self.__result = None
        return self

    def update_headers(self, **kwargs) -> "Api":
        """毫无亮点的更新 headers"""
        self.headers = kwargs
        self.__result = None
        return self

    def update_extra_common(self, **kwargs) -> "Api":
        """毫无亮点的更新 extra_common"""
        self.extra_common = kwargs
        self.__result = None
        return self

    def __prepare_params_data(self) -> None:
        """准备请求参数"""
        new_params, new_data = {}, {}
        for key, value in self.params.items():
            if isinstance(value, bool):
                new_params[key] = int(value)
            elif value is not None:
                new_params[key] = value
        for key, value in self.data.items():
            if isinstance(value, bool):
                new_params[key] = int(value)
            elif value is not None:
                new_data[key] = value
        self.params, self.data = new_params, new_data

    def __prepare_api_data(self) -> None:
        """准备API请求数据"""
        global QIMEI36
        if not QIMEI36:
            QIMEI36 = QIMEI.get_qimei(QQMUSIC_VERSION).q36

        common = {
            "ct": "11",
            "cv": QQMUSIC_VERSION_CODE,
            "v": QQMUSIC_VERSION_CODE,
            "tmeAppID": "qqmusic",
            "QIMEI36": QIMEI36,
            "uid": "3931641530",
            "format": "json",
            "inCharset": "utf-8",
            "outCharset": "utf-8",
        }

        if self.credential:
            if self.verify:
                self.credential.raise_for_no_musickey()
                self.credential.raise_for_no_musicid()

            if self.credential.has_musicid() and self.credential.has_musickey():
                common["qq"] = self.credential.musicid
                common["authst"] = self.credential.musickey
                common["tmeLoginType"] = str(self.credential.login_type)

        common.update(self.extra_common)

        data = {
            "comm": common,
            "request": {
                "module": self.module,
                "method": self.method,
                "param": self.params,
            },
        }
        self.data = data

    def __prepare_request(self) -> dict:
        """准备请求配置参数"""
        config = {
            "url": self.url,
            "method": self.method,
            "data": self.data,
            "params": self.params,
            "headers": HEADERS.copy() if len(self.headers) == 0 else self.headers,
        }
        if self.json_body:
            config["headers"]["Content-Type"] = "application/json"  # type: ignore
            config["data"] = json.dumps(config["data"], ensure_ascii=False).encode()
        if self.module:
            config["method"] = "POST"
            config["params"] = ""
        return config

    async def request(self) -> Union[dict, str, None]:
        """向接口发送请求"""
        if self.module:
            self.__prepare_api_data()
        self.__prepare_params_data()
        config = self.__prepare_request()
        session = get_aiohttp_session()
        try:
            async with session.request(**config) as resp:
                try:
                    resp.raise_for_status()
                except aiohttp.ClientResponseError:
                    raise
                return self.__process_response(resp, await resp.text())
        except aiohttp.ClientConnectionError:
            raise

    def __process_response(self, resp: aiohttp.ClientResponse, resp_text: str) -> Union[dict, str, None]:
        content_length = resp.headers.get("content-length")
        if content_length and int(content_length) == 0:
            return None
        try:
            resp_data = json.loads(resp_text)
            if self.module:
                request_data = resp_data["request"]
                if request_data["code"] != 0:
                    raise ResponseCodeException(
                        request_data["code"],
                        json.dumps(self.data, ensure_ascii=False),
                        request_data["data"],
                    )
                return request_data["data"]
            return resp_data
        except json.JSONDecodeError:
            return resp_text


@atexit.register
def __clean() -> None:
    """程序退出清理操作。"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return

    async def __clean_task():
        s0 = __session_pool.get(loop, None)
        if s0 is not None and not s0.closed:
            await s0.close()

    if loop.is_closed():
        loop.run_until_complete(__clean_task())
    else:
        loop.create_task(__clean_task())
