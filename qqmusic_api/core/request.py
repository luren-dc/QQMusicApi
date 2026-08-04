"""请求描述符与批量请求容器. 提供对 API 请求的抽象与调度."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Generator, Iterable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, TypedDict, TypeVar, cast

import niquests
from niquests.typing import (
    AsyncBodyType,
    AsyncHttpAuthenticationType,
    BodyType,
    CookiesType,
    HeadersType,
    HttpAuthenticationType,
    HttpMethodType,
    MultiPartFilesAltType,
    MultiPartFilesType,
    QueryParameterType,
    TimeoutType,
)
from pydantic import BaseModel
from typing_extensions import Self, overload, override

from ..models.request import Credential
from ..utils.common import bool_to_int
from .exceptions import (
    CgiApiException,
    CredentialExpiredError,
    HTTPError,
    RatelimitedError,
    SignatureRequiredError,
)
from .pagination import ItemPaginatedMixin, ItemT_co, PaginatedMixin
from .versioning import Platform

if TYPE_CHECKING:
    from .client import Client

ResultT = TypeVar("ResultT")
CgiRequestResultT = TypeVar("CgiRequestResultT", bound=BaseModel | dict[str, Any])
HttpRequestResultT = TypeVar("HttpRequestResultT", bound=niquests.Response | BaseModel | dict[str, Any])
ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
NewItemT = TypeVar("NewItemT")
AllowErrorCodes = Literal["all"] | set[int] | frozenset[int] | tuple[int, ...]


@overload
def _build_result(
    raw: dict[str, Any],
    response_model: type[ResponseModel],
) -> ResponseModel: ...


@overload
def _build_result(
    raw: dict[str, Any],
    response_model: None,
) -> dict[str, Any]: ...


def _build_result(
    raw: dict[str, Any],
    response_model: type[BaseModel] | None,
) -> BaseModel | dict[str, Any]:
    """构建响应对象.

    Args:
        raw: 原始响应数据.
        response_model: 期望的响应模型类型, 支持 Pydantic BaseModel.

    Returns:
        构建好的响应模型实例, 或原样返回 (如果无需转换).
    """
    if response_model is None:
        return raw
    if issubclass(response_model, BaseModel):
        return response_model.model_validate(raw)
    return raw


@dataclass(kw_only=True)
class BaseRequest(ABC, Generic[ResultT]):
    """请求描述符基类.

    该基类封装了由客户端执行请求时所需的元数据与行为契约.

    Attributes:
        _client: 请求执行的客户端实例, 用于调度请求.
        response_model: 期望的响应模型类型, 支持 Pydantic BaseModel.
        disable_parse: 是否禁用响应解析, 直接返回原始响应数据.
    """

    _protocol: ClassVar[str] = "cgi"

    _client: "Client"
    response_model: type[BaseModel] | None = None
    disable_parse: bool = False

    def __await__(self) -> Generator[Any, Any, ResultT]:
        """将自身作为载体, 委派给 Client 进行多态调度执行."""
        return self._client.execute(self).__await__()

    @abstractmethod
    def _build_args(self) -> dict[str, Any]:
        """将请求描述符序列化为对应协议所需的底层参数/载荷字典.

        Client 的协议处理器将调用此方法获取参数, 并交由底层引擎发送。
        """
        ...

    @abstractmethod
    def _parse_response(self, raw_data: Any) -> ResultT:
        """解析原始响应数据并返回解析后的结果对象.

        子类应实现此方法以将从网络获得的原始数据转换为
        RequestResultT 指定的类型 (通常为 Pydantic 模型或 dict).

        Args:
            raw_data: 从网络或上游解码后的原始响应数据, 通常为 dict.

        Returns:
            解析得到的结果对象, 类型为 RequestResultT.
        """
        ...


class CgiRequestOptions(TypedDict, total=False):
    """CGI 请求专用的可选配置."""

    comm: dict[str, Any] | None
    override_comm: bool
    preserve_bool: bool
    allow_error_codes: AllowErrorCodes | None
    parse_on_allow: bool
    credential: "Credential | None"
    platform: Platform | None
    sign: bool
    require_login: bool


@dataclass(kw_only=True)
class CgiRequest(BaseRequest[CgiRequestResultT]):
    """CGI 风格的请求述符, 用于封装模块/方法形式的 RPC 请求.

    Attributes:
        module: 请求所属的模块名称.
        method: 请求的方法名称.
        param: 请求参数字典.
        comm: 可选的公共参数, 会与默认公共参数合并或覆盖.
        override_comm: 若为 True, 则直接使用 `comm` 作为公共参数而不合并默认值.
        preserve_bool: 是否在参数中保留布尔值 (而非转换为整型等).
        allow_error_codes: 允许的错误码集合, 如果响应中包含这些错误码,
            将不会抛出异常.
        parse_on_allow: 当响应包含允许的错误码时, 是否仍尝试解析响应数据, 优先级大于 `disable_parse`.
        credential: 可选的凭证对象, 优先于客户端的全局凭证.
        require_login: 请求是否需要凭证.
        platform: 可选的平台标识, 优先于客户端的全局平台设置.
        sign: 指示该请求是否需要签名处理.
    """

    _protocol = "CGI"

    module: str
    method: str
    param: dict[str, Any]
    comm: dict[str, int | str | bool] | None = None
    override_comm: bool = False
    preserve_bool: bool = False
    credential: Credential | None = None
    require_login: bool = False
    platform: Platform | None = None
    sign: bool = False
    allow_error_codes: AllowErrorCodes | None = None
    parse_on_allow: bool = False

    @cached_property
    def _group_key(
        self,
    ) -> tuple[
        Platform | None,
        tuple[tuple[str, int | str | bool], ...] | None,
        bool,
        tuple[int, str],
        bool,
    ]:
        """返回用于批量合并执行的稳定分组键.

        返回值由平台, 公共参数项 (按键排序的 tuple), 是否覆盖公共参数,
        凭证键 (musicid, musickey) 以及签名标志组成, 用于将可合并的请求分组.

        Returns:
            用于分组的不可变元组键.
        """
        platform = self.platform
        credential = self.credential or self._client.credential
        credential_key = (credential.musicid, credential.musickey)
        comm_items = tuple(sorted(self.comm.items(), key=lambda item: item[0])) if self.comm is not None else None
        return (platform, comm_items, self.override_comm, credential_key, self.sign)

    @override
    def _build_args(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "method": self.method,
            "param": self.param if self.preserve_bool else bool_to_int(self.param),
        }

    @override
    def _parse_response(self, raw_data: dict[str, Any]) -> CgiRequestResultT:

        code: int = raw_data.get("code", 0)
        data = raw_data.get("data", {})

        if self.allow_error_codes == "all" or (self.allow_error_codes is not None and code in self.allow_error_codes):
            if self.parse_on_allow:
                return cast("CgiRequestResultT", _build_result(data, self.response_model))
            return cast("CgiRequestResultT", raw_data)

        match code:
            case 2000:
                raise SignatureRequiredError(code=code, data=data)
            case 2001:
                raise RatelimitedError(code=code, data=data)
            case 1000 | 104401 | 104400:
                raise CredentialExpiredError(code=code, data=data)
            case int() if code != 0:
                raise CgiApiException(code=code, data=data)

        if self.disable_parse:
            return cast("CgiRequestResultT", data)
        return cast("CgiRequestResultT", _build_result(data, self.response_model))


class HttpRequestOptions(TypedDict, total=False):
    """HTTP 请求专用的可选配置."""

    files: MultiPartFilesType | MultiPartFilesAltType | None
    auth: HttpAuthenticationType | AsyncHttpAuthenticationType | None
    timeout: TimeoutType | None
    allow_redirects: bool
    stream: bool | None


@dataclass(kw_only=True)
class HttpRequest(BaseRequest[HttpRequestResultT]):
    """标准 HTTP 请求描述符.

    用于封装直接透传到 HTTP 客户端 (如 aiohttp/anyio AsyncSession)
    的请求元数据.

    Attributes:
        url: 请求目标 URL.
        method: HTTP 方法, 如 "GET", "POST" 等.
        params: URL 查询参数字典.
        headers: HTTP 请求头字典.
        cookies: 请求携带的 cookies 字典.
        json: 当以 JSON 方式发送请求体时使用的对象.
        data: 原始请求体数据 (非 JSON 场景, 如表单、二进制等).
        kwargs: 透传给底层 HTTP 客户端的其它可选关键字参数字典.
        credential: 可选的凭证对象, 优先于客户端的全局凭证.
    """

    _protocol = "HTTP"

    method: HttpMethodType
    url: str
    params: QueryParameterType | None = None
    headers: HeadersType | None = None
    cookies: CookiesType | None = None
    json: Any | None = None
    data: BodyType | AsyncBodyType | None = None
    kwargs: HttpRequestOptions | None = None
    credential: Credential | None = None

    @override
    def _build_args(self) -> dict[str, Any]:
        """构建并返回可直接传递给 HTTP 客户端的关键字参数字典.

        Client 在执行路由或多态调度时会调用此方法以获取用于发起网络请求的
        具体参数集合 (例如传递给 AsyncSession.request).

        Returns:
            一个字典, 包含应传递给底层 HTTP 客户端的关键字参数.
        """
        kwargs: dict[str, Any] = {}
        if self.params is not None:
            kwargs["params"] = self.params
        if self.headers is not None:
            kwargs["headers"] = self.headers
        if self.cookies is not None:
            kwargs["cookies"] = self.cookies
        if self.json is not None:
            kwargs["json"] = self.json
        if self.data is not None:
            kwargs["data"] = self.data
        if self.kwargs is not None:
            kwargs.update(self.kwargs)
        return kwargs

    @override
    def _parse_response(self, raw_data: niquests.Response) -> HttpRequestResultT:
        try:
            raw_data.raise_for_status()
        except niquests.HTTPError as http_err:
            status_code = raw_data.status_code or -1
            raise HTTPError(str(http_err), status_code=status_code) from http_err

        if self.disable_parse:
            return cast("HttpRequestResultT", raw_data)

        try:
            parsed_data = raw_data.json()
            return cast("HttpRequestResultT", _build_result(parsed_data, self.response_model))
        except Exception:
            parsed_data = raw_data.text or raw_data.content

        return cast("HttpRequestResultT", parsed_data)


@dataclass(kw_only=True)
class PaginatedCgiRequest(CgiRequest[CgiRequestResultT], PaginatedMixin[CgiRequestResultT]):
    """声明了连续翻页能力的 CGI 请求描述符.

    通过组合 CgiRequest 与 PaginatedMixin, 赋予其自动跨页请求调度能力.
    """

    @override
    @property
    def _page_params(self) -> dict[str, Any]:
        return self.param

    @override
    def _with_page_params(self, params: dict[str, Any]) -> Self:
        return replace(self, param=params)

    def with_extractor(
        self, items_extractor: Callable[[CgiRequestResultT], Iterable[NewItemT]]
    ) -> "ItemPaginatedCgiRequest[CgiRequestResultT, NewItemT]":
        """将当前分页请求转换为能够跨页提取数据项的请求.

        Args:
            items_extractor: 数据项提取函数.

        Returns:
            转换后的带数据提取能力的连续翻页请求描述符.
        """
        from dataclasses import fields

        kwargs = {f.name: getattr(self, f.name) for f in fields(self)}
        return ItemPaginatedCgiRequest(**kwargs, items_extractor=items_extractor)


@dataclass(kw_only=True)
class ItemPaginatedCgiRequest(CgiRequest[CgiRequestResultT], ItemPaginatedMixin[CgiRequestResultT, ItemT_co]):
    """声明了跨页数据项提取能力的连续翻页请求描述符.

    通过组合 CgiRequest 与 ItemPaginatedMixin, 同时具备网络请求、翻页调度与条目流式展开能力.
    """

    items_extractor: Callable[[CgiRequestResultT], Iterable[ItemT_co] | None]

    @property
    @override
    def _page_params(self) -> dict[str, Any]:
        return self.param

    @override
    def _with_page_params(self, params: dict[str, Any]) -> Self:
        return replace(self, param=params)
