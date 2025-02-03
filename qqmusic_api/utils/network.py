"""网络请求"""

import json
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any, ClassVar, Generic, ParamSpec, TypedDict, TypeVar, cast

import httpx

from ..exceptions import CredentialExpiredError, ResponseCodeError, SignInvalidError
from .credential import Credential
from .session import Session, get_session
from .sign import sign

_P = ParamSpec("_P")
_R = TypeVar("_R")

logger = logging.getLogger("qqmusicapi.network")


def _processor(data: dict[str, Any]) -> dict[str, Any]:
    return data


NO_PROCESSOR = _processor


def api_request(
    module: str,
    method: str,
    *,
    verify: bool = False,
    ignore_code: bool = False,
    proceduce_bool: bool = True,
):
    """API请求"""

    def decorator(
        api_func: Callable[_P, Coroutine[None, None, tuple[dict[Any, Any], Callable[[dict[str, Any]], _R]]]],
    ):
        return ApiRequest[_P, _R](
            module,
            method,
            api_func=api_func,
            verify=verify,
            ignore_code=ignore_code,
            proceduce_bool=proceduce_bool,
        )

    return decorator


def _build_common_params(session: Session, credential: Credential | None) -> dict[str, Any]:
    config = session.api_config
    common = {
        "cv": config["version_code"],
        "v": config["version_code"],
        "QIMEI36": session.qimei,
    }
    common.update(ApiRequest.COMMON_DEFAULTS)
    credential = credential or session.credential or Credential()
    if credential.has_musicid() and credential.has_musickey():
        common.update(
            {
                "qq": str(credential.musicid),
                "authst": credential.musickey,
                "tmeLoginType": str(credential.login_type),
            }
        )
    return common


def _set_cookies(credential: Credential | None, session: Session):
    credential = credential or session.credential or Credential()
    if credential.has_musicid() and credential.has_musickey():
        cookies = httpx.Cookies()
        cookies.set("uin", str(credential.musicid), domain="qq.com")
        cookies.set("qqmusic_key", credential.musickey, domain="qq.com")
        cookies.set("qm_keyst", credential.musickey, domain="qq.com")
        cookies.set("tmeLoginType", str(credential.login_type), domain="qq.com")
        session.cookies = cookies


class ApiRequest(Generic[_P, _R]):
    """API 请求处理器"""

    # 公共参数默认值
    COMMON_DEFAULTS: ClassVar = {
        "ct": "11",
        "tmeAppID": "qqmusic",
        "format": "json",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "uid": "3931641530",
    }

    def __init__(
        self,
        module: str,
        method: str,
        api_func: Callable[_P, Coroutine[None, None, tuple[dict[Any, Any], Callable[[dict[str, Any]], _R]]]]
        | None = None,
        *,
        params: dict[str, Any] | None = None,
        common: dict[str, Any] | None = None,
        credential: Credential | None = None,
        verify: bool = False,
        ignore_code: bool = False,
        proceduce_bool: bool = True,
    ) -> None:
        self.module = module
        self.method = method
        self._common = common or {}
        self.params = params or {}
        self.credential = credential
        self.verify = verify
        self.ignore_code = ignore_code
        self.api_func = api_func
        self.proceduce_bool = proceduce_bool
        self.processor: Callable[[dict[str, Any]], Any] = NO_PROCESSOR

    def copy(self) -> "ApiRequest[_P, _R]":
        """创建当前 ApiRequest 实例的副本"""
        req = ApiRequest[_P, _R](
            module=self.module,
            method=self.method,
            api_func=self.api_func,
            params=self.params.copy(),
            common=self._common.copy(),
            credential=self.credential,
            verify=self.verify,
            ignore_code=self.ignore_code,
            proceduce_bool=self.proceduce_bool,
        )
        req.processor = self.processor
        return req

    @property
    def common(self) -> dict[str, Any]:
        """构造公共参数"""
        common = _build_common_params(get_session(), self.credential)
        common.update(self._common)
        return common

    @property
    def data(self) -> dict[str, Any]:
        """构造请求数据体"""
        if self.proceduce_bool:
            params = {k: int(v) if isinstance(v, bool) else v for k, v in self.params.items()}
        else:
            params = self.params

        return {
            "module": self.module,
            "method": self.method,
            "param": params,
        }

    def build_request(self) -> dict[str, Any]:
        """构建请求参数"""
        data = {"comm": self.common}
        data[f"{self.module}.{self.method}"] = self.data

        config = get_session().api_config
        request_params = {
            "url": config["enc_endpoint" if config["enable_sign"] else "endpoint"],
            "json": data,
        }

        if config["enable_sign"]:
            request_params["params"] = {"sign": sign(data)}

        return request_params

    def _process_response(self, resp: httpx.Response) -> dict[str, Any]:
        """处理响应数据"""
        if not resp.content:
            return {}
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return {"data": resp.text}
        req_data = data.get(f"{self.module}.{self.method}", {})
        if self.ignore_code:
            return req_data
        self._validate_response(req_data)
        return req_data.get("data", req_data)

    def _validate_response(self, data: dict[str, Any]) -> None:
        """验证响应状态码"""
        code = data.get("code", 0)
        logger.debug(
            "API %s.%s: %s",
            self.module,
            self.method,
            code,
        )

        if code == 0:
            return

        if code == 2000:
            raise SignInvalidError(data=data)
        if code == 1000:
            raise CredentialExpiredError(self.data, data)
        if code != 0:
            raise ResponseCodeError(code, self.data, data)

    async def request(self) -> dict[str, Any]:
        """执行异步请求"""
        if self.verify:
            if not self.credential:
                raise RuntimeError("缺少 Credential")
            self.credential.raise_for_invalid()

        request = self.build_request()
        logger.debug(f"发起单独请求: {self.module}.{self.method} params: {self.params}")
        _set_cookies(self.credential, get_session())
        resp = await get_session().post(**request)
        resp.raise_for_status()
        return self._process_response(resp)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:  # noqa: D102
        self.credential = cast(Credential, kwargs.pop("credential", self.credential))
        instance = self
        if instance.api_func:
            params, processor = await instance.api_func(*args, **kwargs)
            instance = self.copy()
            instance._common.update(params.pop("common", {}))
            instance.params.update(params)
            instance.processor = processor
        response_data = await instance.request()
        return cast(_R, instance.processor(response_data))

    def __repr__(self) -> str:
        return f"<ApiRequest {self.module}.{self.method}>"


class RequestItem(TypedDict):
    """请求 Item"""

    key: str
    request: ApiRequest
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    processor: Callable[[dict[str, Any]], Any] | None


class RequestGroup:
    """合并多个 API 请求,支持组级公共参数和重复模块方法处理"""

    def __init__(
        self,
        common: dict[str, Any] | None = None,
        credential: Credential | None = None,
    ):
        self._requests: list[RequestItem] = []
        self.common = common.copy() if common else {}
        self.credential = credential
        self._key_counter = defaultdict(int)

    def add_request(self, request: ApiRequest[_P, _R], *args: _P.args, **kwargs: _P.kwargs) -> None:
        """添加请求,自动生成唯一键"""
        base_key = f"{request.module}.{request.method}"
        self._key_counter[base_key] += 1
        count = self._key_counter[base_key]
        unique_key = f"{base_key}.{count}" if count > 1 else base_key

        self._requests.append(
            RequestItem(
                key=unique_key,
                request=request.copy(),
                args=args,
                kwargs=kwargs,
                processor=request.processor,
            )
        )

    def _process_response(self, resp: httpx.Response) -> list[Any]:
        try:
            if not resp.content:
                return []

            results = []
            data = resp.json()

            for req_item in self._requests:
                req = req_item["request"]
                req_data = data.get(req_item["key"], {})
                req._validate_response(req_data)
                if req_item["processor"]:
                    results.append(req_item["processor"](req_data.get("data", req_data)))
                else:
                    results.append(req_data.get("data", req_data))
            return results
        except json.JSONDecodeError:
            return [{"data": resp.text}]

    async def build_request(self):
        """构建请求参数"""
        common = _build_common_params(get_session(), self.credential)
        common.update(self.common)
        merged_data = {"comm": common}
        for req in self._requests:
            if req["request"].api_func:
                params, processor = await req["request"].api_func(*req["args"], **req["kwargs"])
                self.common.update(params.pop("common", {}))
                req["request"].params.update(params)
                req["processor"] = processor
            merged_data[req["key"]] = req["request"].data

        config = get_session().api_config
        request_params = {"url": config["enc_endpoint" if config["enable_sign"] else "endpoint"], "json": merged_data}
        if config["enable_sign"]:
            request_params["params"] = {"sign": sign(merged_data)}

        return request_params

    async def execute(self) -> list[Any]:
        """执行合并请求并返回各请求结果"""
        if not self._requests:
            return []
        request = await self.build_request()
        logger.debug(f"发起合并请求(请求数量: {len(self._requests)}): {request['json']}")
        _set_cookies(self.credential, get_session())
        resp = await get_session().post(**request)
        resp.raise_for_status()
        return self._process_response(resp)
