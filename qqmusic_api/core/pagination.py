"""分页与换一批核心组件定义."""

import copy
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeAlias

from pydantic import BaseModel
from typing_extensions import Self, TypeVar

if TYPE_CHECKING:
    from .request import PaginatedRequest, RefreshableRequest

T_Resp_contra = TypeVar("T_Resp_contra", contravariant=True)
RequestResultT = TypeVar("RequestResultT", bound=BaseModel | dict[str, Any])
ItemT_co = TypeVar("ItemT_co", covariant=True, default=Any)

PaginationParams: TypeAlias = dict[str, Any]
NextParamsBuilder: TypeAlias = Callable[[PaginationParams, T_Resp_contra], PaginationParams | None]


class IteratorStrategy(Protocol[T_Resp_contra]):
    """迭代策略协议."""

    def has_next(self, params: PaginationParams, response: T_Resp_contra) -> bool:
        """判断是否还能继续迭代."""
        ...

    def next_params(self, params: PaginationParams, response: T_Resp_contra) -> PaginationParams:
        """计算并返回下一次请求使用的全新参数字典."""
        ...


class PagerStrategy(IteratorStrategy[T_Resp_contra], Protocol):
    """连续翻页策略协议."""


class RefresherStrategy(IteratorStrategy[T_Resp_contra], Protocol):
    """换一批策略协议."""


class PageStrategy(PagerStrategy[T_Resp_contra], Generic[T_Resp_contra]):
    """基于页码的翻页策略."""

    def __init__(
        self,
        page_key: str,
        *,
        has_more_extractor: Callable[[T_Resp_contra], bool | None] | None = None,
        total_extractor: Callable[[T_Resp_contra], int | None] | None = None,
        page_size: int | None = None,
        start_page: int = 1,
    ) -> None:
        """初始化基于页码的翻页策略.

        Args:
            page_key: 页码参数名.
            has_more_extractor: 是否还有更多数据的提取方式.
            total_extractor: 总数提取方式.
            page_size: 每页条数.
            start_page: 起始页码.
        """
        self.page_key = page_key
        self.has_more_extractor = has_more_extractor
        self.total_extractor = total_extractor
        self.page_size = page_size
        self.start_page = start_page

    def has_next(self, params: PaginationParams, response: T_Resp_contra) -> bool:
        """判断是否还能继续翻页."""
        if self.has_more_extractor is not None:
            explicit_flag = self.has_more_extractor(response)
            if explicit_flag is not None:
                return explicit_flag

        if self.total_extractor is not None and self.page_size is not None:
            total = self.total_extractor(response)
            if total is not None:
                current_page = params.get(self.page_key, self.start_page)
                if not isinstance(current_page, int):
                    raise TypeError("分页请求缺少有效的页码参数, 无法判断是否存在下一页")
                consumed_pages = current_page - self.start_page + 1
                return consumed_pages * self.page_size < total

        return False

    def next_params(self, params: PaginationParams, response: T_Resp_contra) -> PaginationParams:
        """获取下一次请求的参数."""
        new_params = copy.deepcopy(params)
        current_page = new_params.get(self.page_key, self.start_page)
        if not isinstance(current_page, int):
            raise TypeError("分页请求缺少有效的页码参数, 无法计算下一页")
        new_params[self.page_key] = current_page + 1
        return new_params


class OffsetStrategy(PagerStrategy[T_Resp_contra], Generic[T_Resp_contra]):
    """基于偏移量窗口的翻页策略."""

    def __init__(
        self,
        offset_key: str,
        *,
        page_size_key: str | None = None,
        page_size: int | None = None,
        start_offset: int = 0,
        has_more_extractor: Callable[[T_Resp_contra], bool | None] | None = None,
        total_extractor: Callable[[T_Resp_contra], int | None] | None = None,
        count_extractor: Callable[[T_Resp_contra], int | None] | None = None,
    ) -> None:
        """初始化偏移量策略.

        Args:
            offset_key: 偏移量参数名.
            page_size_key: 每页条数参数名.
            page_size: 固定每页条数.
            start_offset: 起始偏移量.
            has_more_extractor: 是否还有更多数据的提取方式.
            total_extractor: 总数提取方式.
            count_extractor: 当前页实际返回数量提取方式.

        Raises:
            ValueError: 当 page_size_key 和 page_size 同时缺失时抛出.
        """
        if page_size_key is None and page_size is None:
            raise ValueError("OffsetStrategy 需要 page_size_key 或 page_size")
        self.offset_key = offset_key
        self.page_size_key = page_size_key
        self.page_size = page_size
        self.start_offset = start_offset
        self.has_more_extractor = has_more_extractor
        self.total_extractor = total_extractor
        self.count_extractor = count_extractor

    def _resolve_page_size(self, params: PaginationParams) -> int:
        if self.page_size is not None:
            return self.page_size
        if self.page_size_key is None:
            raise ValueError("OffsetStrategy 配置错误: page_size_key 和 page_size 不能同时缺失")
        page_size = params.get(self.page_size_key)
        if not isinstance(page_size, int):
            raise TypeError("分页请求缺少有效的 page_size 参数, 无法计算下一页偏移量")
        return page_size

    def _resolve_step(self, params: PaginationParams, response: T_Resp_contra) -> int:
        if self.count_extractor is not None:
            count = self.count_extractor(response)
            if count is not None:
                return count
        return self._resolve_page_size(params)

    def has_next(self, params: PaginationParams, response: T_Resp_contra) -> bool:
        """检查是否有下一页."""
        if self.has_more_extractor is not None:
            explicit_flag = self.has_more_extractor(response)
            if explicit_flag is not None:
                return explicit_flag

        if self.total_extractor is not None:
            total = self.total_extractor(response)
            if total is not None:
                current_offset = params.get(self.offset_key, self.start_offset)
                if current_offset is None:
                    raise ValueError("分页请求缺少有效的 offset 参数, 无法计算下一页")
                step = self._resolve_step(params, response)
                if step <= 0:
                    return False
                return current_offset + step < total

        return False

    def next_params(self, params: PaginationParams, response: T_Resp_contra) -> PaginationParams:
        """获取下一页的请求参数."""
        new_params = copy.deepcopy(params)
        current_offset = new_params.get(self.offset_key, self.start_offset)
        if current_offset is None:
            raise ValueError("分页请求缺少有效的 offset 参数, 无法计算下一页")
        step = self._resolve_step(params, response)
        if step <= 0:
            raise ValueError("分页响应未提供有效的当前页数量, 无法计算下一页偏移量")
        new_params[self.offset_key] = current_offset + step
        return new_params


class BatchRefreshStrategy(RefresherStrategy[T_Resp_contra], Generic[T_Resp_contra]):
    """基于上一批结果标记换一批内容的策略."""

    def __init__(
        self,
        refresh_key: str,
        *,
        cursor_extractor: Callable[[T_Resp_contra], Any],
        has_more_extractor: Callable[[T_Resp_contra], bool | None] | None = None,
    ) -> None:
        """初始化换一批策略.

        Args:
            refresh_key: 下一次请求需要替换的参数名.
            cursor_extractor: 下一批刷新参数提取方式.
            has_more_extractor: 是否还有更多数据的提取方式.
        """
        self.refresh_key = refresh_key
        self.cursor_extractor = cursor_extractor
        self.has_more_extractor = has_more_extractor

    def _extract_refresh_value(self, response: T_Resp_contra) -> Any:
        refresh_value = self.cursor_extractor(response)
        if refresh_value is None:
            raise ValueError("响应未提供换一批所需的刷新参数")
        return refresh_value

    def has_next(self, params: PaginationParams, response: T_Resp_contra) -> bool:
        """检查是否有下一批."""
        if self.has_more_extractor is not None:
            explicit_flag = self.has_more_extractor(response)
            if explicit_flag is not None and not explicit_flag:
                return False

        next_refresh_value = self._extract_refresh_value(response)
        return params.get(self.refresh_key) != next_refresh_value

    def next_params(self, params: PaginationParams, response: T_Resp_contra) -> PaginationParams:
        """获取下一批的请求参数."""
        new_params = copy.deepcopy(params)
        new_params[self.refresh_key] = self._extract_refresh_value(response)
        return new_params


class CursorStrategy(PagerStrategy[T_Resp_contra], Generic[T_Resp_contra]):
    """基于响应游标回写的翻页策略."""

    def __init__(
        self,
        cursor_key: str,
        *,
        cursor_extractor: Callable[[T_Resp_contra], Any],
        has_more_extractor: Callable[[T_Resp_contra], bool | None] | None = None,
    ) -> None:
        """初始化游标翻页策略.

        Args:
            cursor_key: 下一页游标写回的请求参数名.
            cursor_extractor: 下一页游标提取方式.
            has_more_extractor: 是否还有更多数据的提取方式.
        """
        self.cursor_key = cursor_key
        self.cursor_extractor = cursor_extractor
        self.has_more_extractor = has_more_extractor

    def _extract_cursor(self, response: T_Resp_contra) -> Any:
        cursor = self.cursor_extractor(response)
        if cursor is None:
            raise ValueError("分页响应未提供下一页游标, 无法继续翻页")
        return cursor

    def has_next(self, params: PaginationParams, response: T_Resp_contra) -> bool:
        """检查是否有下一页."""
        if self.has_more_extractor is not None:
            explicit_flag = self.has_more_extractor(response)
            if explicit_flag is not None and not explicit_flag:
                return False

        next_cursor = self._extract_cursor(response)
        return params.get(self.cursor_key) != next_cursor

    def next_params(self, params: PaginationParams, response: T_Resp_contra) -> PaginationParams:
        """获取下一页的请求参数."""
        new_params = copy.deepcopy(params)
        new_params[self.cursor_key] = self._extract_cursor(response)
        return new_params


class MultiFieldContinuationStrategy(PagerStrategy[T_Resp_contra], Generic[T_Resp_contra]):
    """基于多字段 continuation 更新的翻页策略."""

    def __init__(
        self,
        build_next_params: NextParamsBuilder[T_Resp_contra],
        *,
        has_more_extractor: Callable[[T_Resp_contra], bool | None] | None = None,
        context_name: str = "continuation",
    ) -> None:
        """初始化多字段延续翻页策略.

        Args:
            build_next_params: 根据当前请求与响应构造下一页完整参数的函数.
            has_more_extractor: 是否还有更多数据的提取方式.
            context_name: 错误上下文中的策略名称.
        """
        self._build_next_params = build_next_params
        self.has_more_extractor = has_more_extractor
        self.context_name = context_name

    def _build_next_params_candidate(
        self, params: PaginationParams, response: T_Resp_contra
    ) -> PaginationParams | None:
        return self._build_next_params(copy.deepcopy(params), response)

    def _resolve_next_params(self, params: PaginationParams, response: T_Resp_contra) -> PaginationParams:
        next_params = self._build_next_params_candidate(params, response)
        if next_params is None:
            raise ValueError(f"[{self.context_name}] 分页响应未提供继续翻页所需的 continuation 数据")
        return next_params

    def has_next(self, params: PaginationParams, response: T_Resp_contra) -> bool:
        """检查是否有下一页."""
        if self.has_more_extractor is not None:
            explicit_flag = self.has_more_extractor(response)
            if explicit_flag is False:
                return False
        return self._build_next_params_candidate(params, response) is not None

    def next_params(self, params: PaginationParams, response: T_Resp_contra) -> PaginationParams:
        """获取下一页的请求参数."""
        return self._resolve_next_params(params, response)


class AsyncPager(Generic[RequestResultT]):
    """有状态异步分页器."""

    def __init__(
        self,
        initial_request: "PaginatedRequest[RequestResultT]",
        limit: int | None = None,
    ) -> None:
        """初始化异步分页器.

        Args:
            initial_request: 初始翻页请求描述符.
            limit: 最大可拉取页数限制.
        """
        self._current_request: PaginatedRequest[RequestResultT] | None = initial_request
        self._limit = limit
        self._yielded_count = 0
        self._has_more = True

    def has_more(self) -> bool:
        """判断是否还有更多页数据可拉取."""
        if self._limit is not None and self._yielded_count >= self._limit:
            return False
        return self._has_more

    async def next(self) -> RequestResultT:
        """拉取并返回下一页响应数据.

        Returns:
            下一页的响应对象.

        Raises:
            StopAsyncIteration: 当没有更多页或达到 limit 时抛出.
        """
        if not self.has_more() or self._current_request is None:
            raise StopAsyncIteration

        req = self._current_request
        response = await req
        self._yielded_count += 1

        self._current_request = req.next_request(response)
        if self._current_request is None:
            self._has_more = False

        return response

    def __aiter__(self) -> Self:
        """返回异步迭代器自身."""
        return self

    async def __anext__(self) -> RequestResultT:
        """异步迭代下一个元素."""
        return await self.next()


class AsyncRefresher(Generic[RequestResultT]):
    """有状态换一批控制器."""

    def __init__(
        self,
        initial_request: "RefreshableRequest[RequestResultT]",
        limit: int | None = None,
    ) -> None:
        """初始化换一批控制器.

        Args:
            initial_request: 初始换一批请求描述符.
            limit: 最大换一批次数限制.
        """
        self._initial_request: RefreshableRequest[RequestResultT] = initial_request
        self._current_request: RefreshableRequest[RequestResultT] | None = initial_request
        self._limit = limit
        self._yielded_count = 0
        self._first_response: RequestResultT | None = None
        self._last_response: RequestResultT | None = None

    def has_more(self) -> bool:
        """判断是否还能继续换一批."""
        if self._limit is not None and self._yielded_count >= self._limit:
            return False
        if self._yielded_count == 0:
            return True
        return self._current_request is not None

    async def first(self) -> RequestResultT:
        """获取或拉取第一批响应数据.

        Returns:
            第一批的响应对象.

        Raises:
            StopAsyncIteration: 当达到 limit 且第一批尚未拉取时抛出.
        """
        if self._first_response is not None:
            return self._first_response

        if not self.has_more():
            raise StopAsyncIteration

        res = await self._initial_request
        self._first_response = res
        if self._yielded_count == 0:
            self._yielded_count = 1
            self._last_response = res
            self._current_request = self._initial_request.next_request(res)
        return res

    async def next(self) -> RequestResultT:
        """拉取并返回下一批响应数据.

        Returns:
            下一批的响应对象.

        Raises:
            StopAsyncIteration: 当没有更多批次或达到 limit 时抛出.
        """
        if not self.has_more() or self._current_request is None:
            raise StopAsyncIteration

        req = self._current_request
        response = await req
        if self._first_response is None:
            self._first_response = response
        self._last_response = response
        self._yielded_count += 1
        self._current_request = req.next_request(response)

        return response

    def __aiter__(self) -> Self:
        """返回异步迭代器自身."""
        return self

    async def __anext__(self) -> RequestResultT:
        """异步迭代下一个元素."""
        return await self.next()
