"""API 客户端核心实现. 整合网络传输、鉴权与业务模块访问."""

from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, Any, Literal, cast, overload

import anyio
from niquests import AsyncSession, AsyncTokenBucketLimiter, PreparedRequest, RetryConfiguration
from niquests.exceptions import RequestException
from niquests.models import Response
from niquests.typing import AsyncHookType, ProxyType, TLSClientCertType, TLSVerifyType
from typing_extensions import Self, sentinel

from ..models.request import Credential
from .api_context import ApiContext
from .exceptions import ApiDataError, NetworkError
from .request import BaseRequest, CgiRequest, HttpRequest, ResultT
from .versioning import Platform

if TYPE_CHECKING:
    from ..modules.album import AlbumApi
    from ..modules.comment import CommentApi
    from ..modules.helper import HelperApi
    from ..modules.login import LoginApi
    from ..modules.lyric import LyricApi
    from ..modules.mv import MvApi
    from ..modules.private_message import PrivateMessageApi
    from ..modules.recommend import RecommendApi
    from ..modules.search import SearchApi
    from ..modules.singer import SingerApi
    from ..modules.song import SongApi
    from ..modules.songlist import SonglistApi
    from ..modules.top import TopApi
    from ..modules.user import UserApi

MISSING = sentinel("MISSING")


class Client:
    """QQMusic API Client."""

    def __init__(
        self,
        credential: Credential | None = None,
        *,
        platform: Platform | None = None,
        device_path: str | None = None,
        rate: float | None = None,
        capacity: float | None = None,
        connect_retries: int | None = None,
        proxies: ProxyType | None = None,
        cert: TLSClientCertType | None = None,
        hooks: AsyncHookType[PreparedRequest | Response] | None = None,
        verify: TLSVerifyType | None = None,
    ):
        """初始化客户端实例.

        Args:
            credential: 全局默认凭证.
            platform: 全局默认请求平台.
            device_path: 设备信息文件路径.
            rate: 请求速率限制 (请求/秒). 默认为 10.
            capacity: 令牌桶容量, 允许的突发请求数. 默认为 50.
            connect_retries: 连接建立失败时的最大重试次数. 默认为 2.
            proxies: 代理配置, 详见 niquests 文档.
            cert: TLS 客户端证书配置, 详见 niquests 文档.
            verify: TLS 证书验证配置, 详见 niquests 文档.
            hooks: 请求/响应钩子, 详见 niquests 文档.
        """
        self._session = AsyncSession(
            multiplexed=True,
            hooks=AsyncTokenBucketLimiter(rate=rate or 10, capacity=capacity or 50),
            happy_eyeballs=True,
            retries=RetryConfiguration(
                total=connect_retries or 2,
                connect=connect_retries or 2,
                read=0,
                redirect=0,
                status=0,
                other=0,
                backoff_factor=0.2,
            ),
            allow_incoming_cookies=False,
        )
        self.proxies = proxies
        self.cert = cert
        self.verify = verify
        self.hooks = hooks

        self._context = ApiContext(credential, platform=platform, device_path=device_path, session=self._session)

    @property
    def credential(self) -> Credential:
        """获取当前全局凭证."""
        return self._context.credential

    @credential.setter
    def credential(self, value: Credential | None):
        self._context.credential = value or Credential()

    @cached_property
    def helper(self) -> "HelperApi":
        """辅助模块."""
        from ..modules.helper import HelperApi

        return HelperApi(self)

    @cached_property
    def comment(self) -> "CommentApi":
        """评论模块."""
        from ..modules.comment import CommentApi

        return CommentApi(self)

    @cached_property
    def private_message(self) -> "PrivateMessageApi":
        """私信模块."""
        from ..modules.private_message import PrivateMessageApi

        return PrivateMessageApi(self)

    @cached_property
    def recommend(self) -> "RecommendApi":
        """推荐模块."""
        from ..modules.recommend import RecommendApi

        return RecommendApi(self)

    @cached_property
    def top(self) -> "TopApi":
        """排行榜模块."""
        from ..modules.top import TopApi

        return TopApi(self)

    @cached_property
    def album(self) -> "AlbumApi":
        """专辑模块."""
        from ..modules.album import AlbumApi

        return AlbumApi(self)

    @cached_property
    def mv(self) -> "MvApi":
        """MV 模块."""
        from ..modules.mv import MvApi

        return MvApi(self)

    @cached_property
    def login(self) -> "LoginApi":
        """登录模块."""
        from ..modules.login import LoginApi

        return LoginApi(self)

    @cached_property
    def search(self) -> "SearchApi":
        """搜索模块."""
        from ..modules.search import SearchApi

        return SearchApi(self)

    @cached_property
    def lyric(self) -> "LyricApi":
        """歌词模块."""
        from ..modules.lyric import LyricApi

        return LyricApi(self)

    @cached_property
    def singer(self) -> "SingerApi":
        """歌手模块."""
        from ..modules.singer import SingerApi

        return SingerApi(self)

    @cached_property
    def song(self) -> "SongApi":
        """歌曲模块."""
        from ..modules.song import SongApi

        return SongApi(self)

    @cached_property
    def songlist(self) -> "SonglistApi":
        """歌单模块."""
        from ..modules.songlist import SonglistApi

        return SonglistApi(self)

    @cached_property
    def user(self) -> "UserApi":
        """用户模块."""
        from ..modules.user import UserApi

        return UserApi(self)

    async def __aenter__(self) -> Self:  # noqa: D105
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: D105
        await self.close()

    async def close(self):
        """关闭客户端连接."""
        await self._session.close()

    async def execute(self, request: BaseRequest[ResultT]) -> ResultT:
        """执行单个请求描述符并解析响应结果.

        Args:
            request: 请求描述符实例.
        """
        match request:
            case CgiRequest():
                if request.require_login:
                    cred = request.credential or self._context.credential
                    if not cred or not cred.musicid or not cred.musickey:
                        from .exceptions import CredentialInvalidError

                        raise CredentialInvalidError("请求需要登录, 未提供有效的登录凭证")

                req_item = request._build_args()

                url, payload, params, headers = await self._context.build_api_kwargs(
                    data=[req_item],
                    comm=request.comm,
                    credential=request.credential,
                    platform=request.platform,
                    override_comm=request.override_comm,
                    sign=request.sign,
                )

                try:
                    resp = await self._session.post(
                        url,
                        json=payload,
                        params=params,
                        headers=headers,
                        proxies=self.proxies,
                        hooks=self.hooks,
                        cert=self.cert,
                        verify=self.verify,
                    )
                    await self._session.gather(resp)
                except RequestException as exc:
                    raise NetworkError(str(exc)) from exc

                raw_data = self._unwrap_cgi_batch(resp, expected_count=1)[0]

                return request._parse_response(raw_data)

            case HttpRequest():
                request = cast("HttpRequest", request)
                kwargs = await self._context.prepare_http_kwargs(
                    credential=request.credential,
                    **request._build_args(),
                )

                try:
                    resp = await self._session.request(
                        request.method,
                        request.url,
                        **kwargs,
                        proxies=self.proxies,
                        hooks=self.hooks,
                        cert=self.cert,
                        verify=self.verify,
                    )
                    await self._session.gather(resp)
                except RequestException as exc:
                    raise NetworkError(str(exc)) from exc

                return request._parse_response(resp)
            case _:
                raise TypeError(f"不支持的请求类型: {type(request)}")

    @overload
    async def gather(
        self,
        requests: list[BaseRequest[ResultT]],
        *,
        batch_size: int = ...,
        return_exceptions: Literal[False] = False,
    ) -> list[ResultT]: ...

    @overload
    async def gather(
        self,
        requests: list[BaseRequest[ResultT]],
        *,
        batch_size: int = ...,
        return_exceptions: Literal[True],
    ) -> list[ResultT | Exception]: ...

    @overload
    async def gather(
        self,
        requests: list[BaseRequest[Any]],
        *,
        batch_size: int = ...,
        return_exceptions: Literal[False] = False,
    ) -> list[Any]: ...

    @overload
    async def gather(
        self,
        requests: list[BaseRequest[Any]],
        *,
        batch_size: int = ...,
        return_exceptions: Literal[True],
    ) -> list[Any | Exception]: ...

    async def gather(
        self,
        requests: list[BaseRequest[Any]],
        *,
        batch_size: int = 20,
        return_exceptions: bool = False,
    ) -> list[Any]:
        """并发执行多个请求描述符并按输入顺序返回解析结果.

        CGI 请求会按可合并条件自动分组, 同一分组内的请求按 `batch_size`
        批量合并为一次 CGI 多参数调用 (req_0, req_1, ...), 以减少网络往返;
        不同分组之间并发执行. HTTP 请求不参与合并, 直接并发执行.

        Args:
            requests: 待执行的请求描述符列表.
            batch_size: 单个 CGI 批量调用 (多参数合并) 包含的最大请求数; 仅对
                CGI 请求生效, 不影响 HTTP 请求.
            return_exceptions: 是否捕捉异常并作为结果返回而不抛出. 为 True 时,
                请求构造、网络传输、响应解析等所有异常都会被写入对应位置的结果;
                为 False 时, 任一请求的异常会以异常组形式抛出.

        Returns:
            与 `requests` 顺序一致的解析结果列表. 当 `return_exceptions` 为
            True 时, 失败位置的结果为对应的异常对象.

        Raises:
            ValueError: 当 `batch_size` 小于等于 0 时抛出.
            ExceptionGroup: 当 `return_exceptions` 为 False 且任一请求执行
                期间发生异常时, 其余并发请求会被取消, 失败异常会以异常组的
                形式抛出 (anyio 将异常包装为 `ExceptionGroup`, 它是
                `BaseExceptionGroup` 的子类; 即使只有一个请求失败也会被包装
                成异常组; 多个请求同时各自抛出异常时, 异常组可能包含多个
                异常).
            ApiDataError: 当内部依赖的结果未能完整回填时抛出 (一般不应发生).
        """
        if batch_size <= 0:
            raise ValueError("batch_size 必须大于 0")
        if not requests:
            return []

        results: list[Any] = [MISSING] * len(requests)
        all_task: defaultdict[str, list[tuple[int, BaseRequest[Any]]]] = defaultdict(list)
        for idx, req in enumerate(requests):
            all_task[req._protocol].append((idx, req))

        async def _gather_cgi(tasks: list[tuple[int, CgiRequest]]):
            batch_responses = []
            grouped_indices: defaultdict[Any, list[tuple[int, CgiRequest[Any]]]] = defaultdict(list)
            for orig_idx, req in tasks:
                if req.require_login:
                    cred = req.credential or self._context.credential
                    if not cred or not cred.musicid or not cred.musickey:
                        from .exceptions import CredentialInvalidError

                        exc = CredentialInvalidError("请求需要登录, 未提供有效的登录凭证")
                        if return_exceptions:
                            results[orig_idx] = exc
                            continue
                        raise exc
                grouped_indices[req._group_key].append((orig_idx, req))

            for group in grouped_indices.values():
                base_req = group[0][1]
                for start in range(0, len(group), batch_size):
                    chunk = group[start : start + batch_size]
                    chunk_orig_indices = [item[0] for item in chunk]

                    url, payload, params, headers = await self._context.build_api_kwargs(
                        data=[r[1]._build_args() for r in chunk],
                        comm=base_req.comm,
                        credential=base_req.credential,
                        platform=base_req.platform,
                        override_comm=base_req.override_comm,
                        sign=base_req.sign,
                    )

                    try:
                        resp = await self._session.post(
                            url,
                            json=payload,
                            params=params,
                            headers=headers,
                            proxies=self.proxies,
                            hooks=self.hooks,
                            cert=self.cert,
                            verify=self.verify,
                        )
                    except RequestException as exc:
                        error = NetworkError(str(exc))
                        if return_exceptions:
                            for req_index in chunk_orig_indices:
                                results[req_index] = error
                            continue
                        raise error from exc
                    batch_responses.append((chunk_orig_indices, resp))

            if not batch_responses:
                return

            try:
                await self._session.gather(*(resp for _, resp in batch_responses))
            except RequestException as exc:
                error = NetworkError(str(exc))
                if return_exceptions:
                    for batch_indices, _ in batch_responses:
                        for req_index in batch_indices:
                            results[req_index] = error
                    return
                raise error from exc

            for batch_indices, response in batch_responses:
                try:
                    data = self._unwrap_cgi_batch(response, len(batch_indices))
                except Exception as exc:
                    if return_exceptions:
                        for req_index in batch_indices:
                            results[req_index] = exc
                        continue
                    raise

                for batch_index, req_index in enumerate(batch_indices):
                    request = cast("CgiRequest", requests[req_index])
                    try:
                        results[req_index] = request._parse_response(data[batch_index])
                    except Exception as exc:
                        if return_exceptions:
                            results[req_index] = exc
                        else:
                            raise

        async def _gather_http(tasks: list[tuple[int, HttpRequest]]):
            http_responses = []
            for orig_idx, req in tasks:
                kwargs = await self._context.prepare_http_kwargs(
                    credential=req.credential,
                    **req._build_args(),
                )

                try:
                    resp = await self._session.request(
                        req.method,
                        req.url,
                        **kwargs,
                        proxies=self.proxies,
                        hooks=self.hooks,
                        cert=self.cert,
                        verify=self.verify,
                    )
                except RequestException as exc:
                    error = NetworkError(str(exc))
                    if return_exceptions:
                        results[orig_idx] = error
                        continue
                    raise error from exc
                http_responses.append((orig_idx, req, resp))

            if not http_responses:
                return

            try:
                await self._session.gather(*(resp for _, _, resp in http_responses))
            except RequestException as exc:
                error = NetworkError(str(exc))
                if return_exceptions:
                    for orig_idx, _, _ in http_responses:
                        results[orig_idx] = error
                    return
                raise error from exc

            for orig_idx, req, resp in http_responses:
                try:
                    results[orig_idx] = req._parse_response(resp)
                except Exception as exc:  # noqa: PERF203
                    if return_exceptions:
                        results[orig_idx] = exc
                    else:
                        raise

        async with anyio.create_task_group() as tg:
            for protocol, tasks in all_task.items():
                if protocol == CgiRequest._protocol:
                    tasks = cast("list[tuple[int, CgiRequest]]", tasks)
                    tg.start_soon(_gather_cgi, tasks)
                elif protocol == HttpRequest._protocol:
                    tasks = cast("list[tuple[int, HttpRequest]]", tasks)
                    tg.start_soon(_gather_http, tasks)

        missing = [i for i, res in enumerate(results) if res is MISSING]
        if missing:
            raise ApiDataError(f"缺少以下索引结果: {missing}")

        return results

    def _unwrap_cgi_batch(self, response: Response, expected_count: int) -> list[dict[str, Any]]:
        """拆解并校验 CGI 批量响应的外层信封."""
        from .exceptions import ApiDataError, GlobalApiError, HTTPError

        if response.status_code != 200:
            raise HTTPError(
                f"HTTP 请求状态码异常: {response.status_code}",
                status_code=cast("int", response.status_code),
            )
        if not response.content:
            raise ApiDataError("响应无内容")
        try:
            resp = response.json()
        except Exception as exc:
            raise ApiDataError("响应内容非有效 JSON 格式") from exc
        code: int = cast("dict", resp).pop("code", 0)

        if code != 0:
            raise GlobalApiError("Module 请求失败", code=code, data=response.text)

        try:
            return [resp[f"req_{i}"] for i in range(expected_count)]
        except KeyError as exc:
            raise ApiDataError(f"CGI 响应格式异常, 缺少预期的子响应: {exc}") from exc
