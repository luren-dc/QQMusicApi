"""网络请求"""

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Union

import httpx

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from ..exceptions import CredentialExpiredError, ResponseCodeError, SignInvalidError
from .credential import Credential
from .session import get_session
from .sign import sign


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

    url: str = field(default="")
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
        self.original_params = self.params.copy()
        self.original_data = self.data.copy()
        self.data = {k: None for k in self.data}
        self.params = {k: None for k in self.params}
        self.extra_common = {k: None for k in self.extra_common}
        self._result: Optional[dict] = None
        self._session = get_session()
        self._cookies = httpx.Cookies()

        if not self.credential.has_musicid():
            self.credential = self._session.credential

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

        if self._session.api_config["enable_sign"]:
            self.url = self._session.api_config["enc_endpoint"]
        else:
            self.url = self._session.api_config["endpoint"]

        common_data = {
            "ct": "11",
            "cv": self._session.api_config["version_code"],
            "v": self._session.api_config["version_code"],
            "tmeAppID": "qqmusic",
            "QIMEI36": self._session.qimei,
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

    def _sign(self):
        if not self.module:
            return

        if self._session.api_config["enable_sign"]:
            self.url = self._session.api_config["enc_endpoint"]
            self.params["sign"] = sign(self.data)
        else:
            self.url = self._session.api_config["endpoint"]

    def _prepare_request(self) -> dict:
        """准备请求"""
        self._prepare_params_data()
        self._prepare_api_data()
        self._prepare_credential()
        self._sign()

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

        logger.debug(
            f"发起请求: {self.url} {self.module} {self.method} {self.module} params: {self.params} data: {self.data}"
        )

        resp = await self._session.request(**config)
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
        from .. import logger

        # 是否忽略响应代码
        if self.ignore_code:
            return resp
        code = resp["code"]

        if self.module:
            logger.debug(
                "API %s.%s: %s",
                self.module,
                self.method,
                code,
            )

        if code == 2000:
            raise SignInvalidError(data=resp)
        if code == 1000:
            raise CredentialExpiredError(self.data, resp)
        if code != 0:
            raise ResponseCodeError(code, self.data, resp)

        return resp.get("data", resp)
