"""请求描述符与批量请求容器. 提供对 API 请求的抽象与调度."""

import copy
from collections.abc import Generator
from dataclasses import dataclass
from dataclasses import replace as dc_replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from pydantic import BaseModel
from typing_extensions import Self, overload

from ..models.request import Credential
from .pagination import PagerStrategy, RefresherStrategy
from .versioning import Platform

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from .client import Client

RequestResultT = TypeVar("RequestResultT", bound=BaseModel | dict[str, Any])
ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
AllowErrorCodes = Literal["all"] | set[int] | frozenset[int] | tuple[int, ...]


@overload
def _build_result(
    raw: dict[str, Any],
    response_model: type["ResponseModel"],
) -> "ResponseModel": ...


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
class Request(Generic[RequestResultT]):
    """请求描述符."""

    _client: "Client"
    module: str
    method: str
    param: dict[str, Any] | dict[int, Any]
    response_model: type[BaseModel] | None = None
    comm: dict[str, int | str | bool] | None = None
    override_comm: bool = False
    preserve_bool: bool = False
    credential: Credential | None = None
    platform: Platform | None = None
    allow_error_codes: AllowErrorCodes | None = None
    parse_on_allow: bool = False
    sign: bool = False

    def __await__(self) -> Generator[Any, Any, RequestResultT]:
        """使 Request 对象可被 await 执行."""
        return self._client.execute(self).__await__()

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
        """返回可批量合并执行的稳定分组键."""
        platform = self.platform
        credential = self.credential or self._client.credential
        credential_key = (credential.musicid, credential.musickey)
        comm_items = tuple(sorted(self.comm.items(), key=lambda item: item[0])) if self.comm is not None else None
        return (platform, comm_items, self.override_comm, credential_key, self.sign)

    def replace(self, **changes: Any) -> Self:
        """返回一个应用了修改的新 Request 对象, 不会修改原对象."""
        if "param" not in changes:
            changes["param"] = copy.deepcopy(self.param)
        if "comm" not in changes and self.comm is not None:
            changes["comm"] = copy.deepcopy(self.comm)
        if "override_comm" not in changes:
            changes["override_comm"] = self.override_comm
        return dc_replace(self, **changes)


@dataclass
class PaginatedRequest(Request[RequestResultT]):
    """声明了连续翻页能力的请求描述符."""

    pager_strategy: PagerStrategy[Any, RequestResultT]

    async def paginate(self, limit: int | None = None) -> "AsyncGenerator[RequestResultT, None]":
        """返回响应的分页迭代器.

        Args:
            limit: 最大获取页数.
        """
        current_request: Request[RequestResultT] | None = self
        yielded_count = 0
        while current_request is not None:
            if limit is not None and yielded_count >= limit:
                break
            response = await current_request
            yield response
            yielded_count += 1

            if self.pager_strategy.has_next(current_request.param, response):
                next_param = self.pager_strategy.next_params(current_request.param, response)
                current_request = current_request.replace(param=next_param)
            else:
                current_request = None

    def __aiter__(self) -> "AsyncGenerator[RequestResultT, None]":
        """返回异步迭代器自身."""
        return self.paginate()


@dataclass
class RefreshableRequest(Request[RequestResultT]):
    """声明了换一批能力的请求描述符."""

    refresh_strategy: RefresherStrategy[Any, RequestResultT]

    def next_request(self, previous_response: RequestResultT) -> "RefreshableRequest[RequestResultT] | None":
        """根据上一次请求的响应, 构建下一次换一批的请求.

        Args:
            previous_response: 上一次请求得到的响应.

        Returns:
            下一次请求的描述符, 如果没有更多则返回 None.
        """
        if self.refresh_strategy.has_next(self.param, previous_response):
            next_param = self.refresh_strategy.next_params(self.param, previous_response)
            return self.replace(param=next_param)
        return None
