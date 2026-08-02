"""API 模块基类."""

from typing import TYPE_CHECKING, Any, overload

from ..core.exceptions import CredentialInvalidError
from ..core.pagination import PagerStrategy
from ..core.request import (
    AllowErrorCodes,
    PaginatedRequest,
    Request,
    ResponseModel,
)
from ..core.versioning import Platform

if TYPE_CHECKING:
    from ..core.client import Client
    from ..models.request import Credential


class ApiModule:
    """API 模块基类."""

    def __init__(self, client: "Client") -> None:
        self._client = client
        self._session = client._session

    def _require_login(self, credential: "Credential | None" = None):
        """获取并校验登录凭证.

        Args:
            credential: 待校验的凭证, 若不提供则使用客户端当前凭证.

        Returns:
            Credential: 校验通过的凭证对象.

        Raises:
            CredentialInvalidError: 如果凭证中缺少必要的 musicid 或 musickey.
        """
        target_credential = credential or self._client.credential
        if not target_credential.musicid or not target_credential.musickey:
            raise CredentialInvalidError("接口需要有效登录凭证")
        return target_credential

    async def _request(
        self,
        method: str,
        url: str,
        credential: "Credential | None" = None,
        platform: Platform | None = None,
        *,
        lazy: bool = False,
        **kwargs: Any,
    ):
        """发送请求并自动携带对应凭证与平台 User-Agent.

        Args:
            method: HTTP 方法, 如 "GET" 或 "POST".
            url: 目标 URL.
            credential: 请求凭证 (默认使用客户端凭证).
            platform: 请求平台 (默认使用客户端平台).
            lazy: 是否延迟发送请求.
            **kwargs: 透传给底层客户端的参数.

        Returns:
            httpx.Response: 响应对象.
        """
        return await self._client.request(
            method=method,
            url=url,
            credential=credential,
            platform=platform,
            lazy=lazy,
            **kwargs,
        )

    def _build_query_common_params(self, platform: Platform | None = None) -> dict[str, int]:
        """构建查询接口使用的通用版本参数."""
        profile = self._client._version_policy.get_profile(platform or self._client.platform)
        return {"ct": profile.ct, "cv": profile.cv}

    @overload
    def _build_request(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        response_model: None = None,
        comm: dict[str, Any] | None = None,
        *,
        override_comm: bool = False,
        preserve_bool: bool = False,
        credential: "Credential | None" = None,
        platform: Platform | None = None,
        allow_error_codes: AllowErrorCodes | None = None,
        parse_on_allow: bool = False,
        pager_strategy: None = None,
        sign: bool = False,
        require_login: bool = False,
    ) -> Request[dict[str, Any]]: ...

    @overload
    def _build_request(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        response_model: None = None,
        comm: dict[str, Any] | None = None,
        *,
        override_comm: bool = False,
        preserve_bool: bool = False,
        credential: "Credential | None" = None,
        platform: Platform | None = None,
        allow_error_codes: AllowErrorCodes | None = None,
        parse_on_allow: bool = False,
        pager_strategy: PagerStrategy[dict[str, Any]],
        sign: bool = False,
        require_login: bool = False,
    ) -> PaginatedRequest[dict[str, Any]]: ...

    @overload
    def _build_request(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        response_model: type[ResponseModel],
        comm: dict[str, Any] | None = None,
        *,
        override_comm: bool = False,
        preserve_bool: bool = False,
        credential: "Credential | None" = None,
        platform: Platform | None = None,
        allow_error_codes: AllowErrorCodes | None = None,
        parse_on_allow: bool = False,
        pager_strategy: None = None,
        sign: bool = False,
        require_login: bool = False,
    ) -> Request[ResponseModel]: ...

    @overload
    def _build_request(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        response_model: type[ResponseModel],
        comm: dict[str, Any] | None = None,
        *,
        override_comm: bool = False,
        preserve_bool: bool = False,
        credential: "Credential | None" = None,
        platform: Platform | None = None,
        allow_error_codes: AllowErrorCodes | None = None,
        parse_on_allow: bool = False,
        pager_strategy: PagerStrategy[ResponseModel],
        sign: bool = False,
        require_login: bool = False,
    ) -> PaginatedRequest[ResponseModel]: ...

    def _build_request(
        self,
        module: str,
        method: str,
        param: dict[str, Any],
        response_model: type[ResponseModel] | None = None,
        comm: dict[str, Any] | None = None,
        *,
        override_comm: bool = False,
        preserve_bool: bool = False,
        credential: "Credential | None" = None,
        platform: Platform | None = None,
        allow_error_codes: AllowErrorCodes | None = None,
        parse_on_allow: bool = False,
        pager_strategy: PagerStrategy[Any] | None = None,
        sign: bool = False,
        require_login: bool = False,
    ) -> Request[Any] | PaginatedRequest[Any]:
        """构建可 await 的请求描述符.

        Args:
            module: 接口所属的模块名称.
            method: 接口调用的方法名称.
            param: 请求的核心业务参数.
            response_model: 用于解析响应数据的 Pydantic 模型.
            comm: 附加的通用请求参数. 行为受 `override_comm` 影响.
            override_comm: 为 True 时, `comm` 将彻底替代自动生成的参数; 为 False 时, 将与生成参数进行合并更新.
            preserve_bool: 是否保留布尔值原样 (默认转为 0/1 整型).
            credential: 本次请求专用的凭证. 默认使用客户端当前凭证.
            platform: 本次请求的平台标识. 默认使用客户端所属平台.
            allow_error_codes: 允许放行的业务非零错误码.
            parse_on_allow: 为 True 时, 匹配 `allow_error_codes` 的响应仍走模型解析而非返回原始字典.
            pager_strategy: 分页策略描述符. 提供后则升级为 `PaginatedRequest`.
            sign: 是否对请求进行签名.
            require_login: 为 True 时, 在构建请求前校验凭证有效性.

        Returns:
            组装好的 Request 或衍生子类描述符.

        Raises:
            CredentialInvalidError: 如果 require_login 为 True 且凭证无效时抛出.
        """
        from ..core.request import PaginatedRequest, Request

        if require_login:
            credential = self._require_login(credential)

        common_kwargs = {
            "_client": self._client,
            "module": module,
            "method": method,
            "param": param,
            "response_model": response_model,
            "comm": comm,
            "override_comm": override_comm,
            "preserve_bool": preserve_bool,
            "credential": credential,
            "platform": platform,
            "allow_error_codes": allow_error_codes,
            "parse_on_allow": parse_on_allow,
            "sign": sign,
        }
        if pager_strategy is not None:
            return PaginatedRequest(**common_kwargs, pager_strategy=pager_strategy)
        return Request(**common_kwargs)
