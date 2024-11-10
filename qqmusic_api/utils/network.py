"""网络请求"""

import asyncio
import atexit
import json
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Union

import httpx
from typing_extensions import Self

from ..exceptions import CredentialExpiredError, ResponseCodeError
from .credential import Credential
from .qimei import QIMEI

QQMUSIC_API = "https://u.y.qq.com/cgi-bin/musicu.fcg"
QQMUSIC_VERSION = "13.2.5.8"
QQMUSIC_VERSION_CODE = 13020508
QIMEI36 = None

_SESSION_POOL: dict[asyncio.AbstractEventLoop, httpx.AsyncClient] = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54",
}


def get_qimei() -> str:
    """获取 QIMEI

    Returns:
        QIMEI
    """
    global QIMEI36
    if not QIMEI36:
        QIMEI36 = QIMEI.get_qimei(QQMUSIC_VERSION).q36
    return QIMEI36


def get_session() -> httpx.AsyncClient:
    """获取当前 EventLoop 的 Session，用于自定义请求

    Returns:
        httpx.AsyncClient
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    if loop in _SESSION_POOL:
        return _SESSION_POOL[loop]
    else:
        session = httpx.AsyncClient(timeout=20)
        _SESSION_POOL[loop] = session
        return session


def set_session(session: httpx.AsyncClient) -> None:
    """设置当前 EventLoop 的 Session

    Args:
        session: Session
    """
    loop = asyncio.get_event_loop()
    _SESSION_POOL[loop] = session


@dataclass
class Api:
    """API 请求类

    Attributes:
        url: 请求地址
        method: 请求方法
        module: 请求模块
        params: 请求参数
        data: 请求数据
        headers: 请求头
        json_body: 是否使用 json 作为载荷
        verify: 是否验证凭据
        platform: API 来源
        ignore_code: 是否忽略返回值 code 检验直接返回
        extra_common: 额外参数
        credential: 账号凭据
        comment: API 注释
    """

    url: str = field(default=QQMUSIC_API)
    method: str = field(default="GET")
    module: str = field(default="")
    params: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    json_body: bool = field(default=False)
    verify: bool = field(default=False)
    platform: Literal["mobile", "desktop", "web"] = field(default="mobile")
    ignore_code: bool = field(default=False)
    extra_common: dict = field(default_factory=dict)
    credential: Credential = field(default_factory=Credential)
    comment: str = field(default="")

    def __post_init__(self):
        if not self.module:
            self.method = self.method.upper()
        if not self.headers:
            self.headers = HEADERS
        self.original_params = self.params.copy()
        self.original_data = self.data.copy()
        self.data = {k: None for k in self.data}
        self.params = {k: None for k in self.params}
        self.extra_common = {k: None for k in self.extra_common}
        self._result: Optional[dict] = None
        self._session = get_session()
        self._cookies = httpx.Cookies()

    def _setattr_(self, name: str, value: Any, /) -> None:
        if name != "_result" and hasattr(self, "_result"):
            self._result = None
        return super().__setattr__(name, value)

    def update_params(self, **kwargs) -> Self:
        """更新参数"""
        self.params.update(kwargs)
        return self

    def update_data(self, **kwargs) -> Self:
        """更新数据"""
        self.data.update(kwargs)
        return self

    def update_extra_common(self, **kwargs) -> Self:
        """更新额外参数"""
        self.extra_common.update(kwargs)
        return self

    def update_headers(self, **kwargs) -> Self:
        """更新请求头"""
        self.headers.update(kwargs)
        return self

    def update_cookies(self, cookies: httpx.Cookies) -> Self:
        """更新 Cookies"""
        self._cookies.update(cookies)
        return self

    def _prepare_params_data(self) -> None:
        """准备请求参数"""
        new_params, new_data = {}, {}
        for key, value in self.params.items():
            if isinstance(value, bool):
                new_params[key] = int(value)
            elif value is not None:
                new_params[key] = value
        for key, value in self.data.items():
            if isinstance(value, bool):
                new_data[key] = int(value)
            elif value is not None:
                new_data[key] = value
        self.params, self.data = new_params, new_data

    def _prepare_api_data(self) -> None:
        """准备 API 数据"""
        if not self.module:
            return

        common_data = {
            "ct": "11",
            "cv": QQMUSIC_VERSION_CODE,
            "v": QQMUSIC_VERSION_CODE,
            "tmeAppID": "qqmusic",
            "QIMEI36": get_qimei(),
            "uid": "3931641530",
            "format": "json",
            "inCharset": "utf-8",
            "outCharset": "utf-8",
            **self.extra_common,
        }

        # 组装请求数据
        self.data = {
            "comm": common_data,
            "request": {
                "module": self.module,
                "method": self.method,
                "param": self.params.copy(),
            },
        }

        self.json_body = True
        self.params.clear()

    def _prepare_credential(self) -> None:
        """准备账号凭据"""
        if self.verify:
            self.credential.raise_for_invalid()

        if not self.credential.has_musicid() or not self.credential.has_musickey():
            return

        if self.module:
            common = self.data["comm"]
            common["qq"] = str(self.credential.musicid)
            common["authst"] = self.credential.musickey
            common["tmeLoginType"] = str(self.credential.login_type)
        else:
            cookies = {
                "uin": str(self.credential.musicid),
                "qqmusic_key": self.credential.musickey,
                "qm_keyst": self.credential.musickey,
                "tmeLoginType": str(self.credential.login_type),
            }
            self._cookies.update(cookies)

    def _prepare_request(self) -> dict:
        """准备请求"""
        self._prepare_params_data()
        self._prepare_api_data()
        self._prepare_credential()

        self.headers.update({"Cookie": "; ".join([f"{k}={v}" for k, v in self._cookies.items()])})

        config = {
            "url": self.url,
            "method": self.method if not self.module else "POST",
            "params": self.params,
            "headers": self.headers,
        }
        if self.json_body:
            config["json"] = self.data
        else:
            config["data"] = self.data
        return config

    async def request(self) -> httpx.Response:
        """发起请求"""
        from .. import logger

        config = self._prepare_request()
        logger.debug("发起请求: %s", config)
        resp = await self._session.request(**config)
        if not self.ignore_code:
            resp.raise_for_status()
        self._session.cookies.clear()
        return resp

    def _process_response(self, resp: httpx.Response) -> Union[None, str, dict]:
        """处理响应"""
        content_length = resp.headers.get("Content-Length")
        if content_length and int(content_length) == 0:
            return None
        try:
            return resp.json()
        except json.decoder.JSONDecodeError:
            return resp.text

    async def fetch(self) -> Union[None, str, dict]:
        """发起请求并处理响应"""
        return self._process_response(await self.request())

    @property
    async def result(self) -> dict:
        """获取请求结果"""
        if self._result:
            return self._result
        resp = await self.fetch()

        # 处理响应
        if isinstance(resp, dict):
            # 判断是否为标准请求
            if self.module:
                request_data = resp["request"]
                # 处理响应代码
                self._result = self._process_response_code(request_data)
            else:
                if resp.get("code", None) is not None:
                    self._result = self._process_response_code(resp)
                else:
                    self._result = dict(resp.get("data", resp))
        else:
            # 包装非 JSON 响应
            self._result = {"data": resp}
        return self._result

    def _process_response_code(self, resp: dict) -> dict:
        """处理响应代码"""
        # 是否忽略响应代码
        if self.ignore_code:
            return resp
        code = resp["code"]
        if code == 1000:
            raise CredentialExpiredError(self.data, resp)
        elif code != 0:
            raise ResponseCodeError(code, self.data, resp)
        return resp.get("data", resp)


@atexit.register
def _clean() -> None:
    """程序退出清理操作。"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return

    async def _clean_task():
        s0 = _SESSION_POOL.get(loop, None)
        if s0 is not None and not s0.is_closed:
            await s0.aclose()

    if not loop.is_closed():
        loop.run_until_complete(_clean_task())
    else:
        asyncio.run(_clean_task())
