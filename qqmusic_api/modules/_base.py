"""API 模块基类."""

from http.cookiejar import CookieJar
from typing import TYPE_CHECKING, Any, Literal, TypedDict, overload

import niquests
from typing_extensions import Unpack

from ..core.pagination import PagerStrategy
from ..core.request import (
    AllowErrorCodes,
    CgiRequest,
    HttpRequest,
    PaginatedCgiRequest,
    ResponseModel,
)
from ..core.versioning import Platform

if TYPE_CHECKING:
    from ..core.client import Client
    from ..models.request import Credential


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


class HttpRequestOptions(TypedDict, total=False):
    """HTTP 请求专用的可选配置."""

    params: dict[str, Any] | None
    headers: dict[str, str] | None
    cookies: dict[str, str] | CookieJar | None
    json: Any | None
    data: Any | None
    kwargs: dict[str, Any] | None
    credential: "Credential | None"


class ApiModule:
    """API 模块基类."""

    def __init__(self, client: "Client") -> None:
        self._client = client
        self._session = client._session

    def _build_version_params(self, platform: Platform | None = None) -> dict[str, int]:
        """构建查询接口使用的版本参数."""
        profile = self._client._context.version_policy.get_profile(platform or self._client._context.platform)
        return {"ct": profile.ct, "cv": profile.cv}

    @overload
    def _build_cgi(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        *,
        disable_parse: Literal[True],
        pager_strategy: PagerStrategy[dict[str, Any]],
        response_model: type[ResponseModel] | None = None,
        **options: Unpack[CgiRequestOptions],
    ) -> PaginatedCgiRequest[dict[str, Any]]: ...

    @overload
    def _build_cgi(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        *,
        disable_parse: Literal[True],
        response_model: type[ResponseModel] | None = None,
        **options: Unpack[CgiRequestOptions],
    ) -> CgiRequest[dict[str, Any]]: ...

    @overload
    def _build_cgi(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        *,
        response_model: type[ResponseModel],
        pager_strategy: PagerStrategy[ResponseModel],
        disable_parse: Literal[False] = False,
        **options: Unpack[CgiRequestOptions],
    ) -> PaginatedCgiRequest[ResponseModel]: ...

    @overload
    def _build_cgi(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        *,
        response_model: type[ResponseModel],
        disable_parse: Literal[False] = False,
        **options: Unpack[CgiRequestOptions],
    ) -> CgiRequest[ResponseModel]: ...

    @overload
    def _build_cgi(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        *,
        pager_strategy: PagerStrategy[dict[str, Any]],
        disable_parse: Literal[False] = False,
        **options: Unpack[CgiRequestOptions],
    ) -> PaginatedCgiRequest[dict[str, Any]]: ...

    @overload
    def _build_cgi(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        *,
        disable_parse: Literal[False] = False,
        **options: Unpack[CgiRequestOptions],
    ) -> CgiRequest[dict[str, Any]]: ...

    def _build_cgi(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        *,
        response_model: type[ResponseModel] | None = None,
        pager_strategy: PagerStrategy[Any] | None = None,
        disable_parse: bool = False,
        **options: Unpack[CgiRequestOptions],
    ) -> CgiRequest[Any] | PaginatedCgiRequest[Any]:
        """构建可 await 的 CGI 请求描述符."""
        if pager_strategy is not None:
            return PaginatedCgiRequest(
                _client=self._client,
                module=module,
                method=method,
                param=param,
                response_model=response_model,
                pager_strategy=pager_strategy,
                disable_parse=disable_parse,
                **options,
            )

        return CgiRequest(
            _client=self._client,
            module=module,
            method=method,
            param=param,
            response_model=response_model,
            disable_parse=disable_parse,
            **options,
        )

    @overload
    def _build_http(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        url: str,
        *,
        disable_parse: Literal[True],
        response_model: type[ResponseModel] | None = ...,
        **options: Unpack[HttpRequestOptions],
    ) -> HttpRequest[niquests.Response]: ...

    @overload
    def _build_http(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        url: str,
        *,
        response_model: type[ResponseModel],
        disable_parse: Literal[False] = False,
        **options: Unpack[HttpRequestOptions],
    ) -> HttpRequest[ResponseModel]: ...

    @overload
    def _build_http(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        url: str,
        *,
        response_model: None = None,
        disable_parse: Literal[False] = False,
        **options: Unpack[HttpRequestOptions],
    ) -> HttpRequest[dict[str, Any]]: ...

    def _build_http(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
        url: str,
        *,
        response_model: type[ResponseModel] | None = None,
        disable_parse: bool = False,
        **options: Unpack[HttpRequestOptions],
    ) -> HttpRequest[Any]:
        """构建可 await 的标准 HTTP 请求描述符."""
        return HttpRequest(
            _client=self._client,
            method=method,
            url=url,
            response_model=response_model,
            disable_parse=disable_parse,
            **options,
        )
