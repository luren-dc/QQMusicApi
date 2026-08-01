"""分页与换一批策略单元测试."""

from dataclasses import dataclass, field
from typing import Any, cast

import pytest
from pydantic import BaseModel

from qqmusic_api.core.pagination import (
    BatchRefreshStrategy,
    CursorStrategy,
    MultiFieldContinuationStrategy,
    OffsetStrategy,
    PageStrategy,
)
from qqmusic_api.core.request import PaginatedRequest, RefreshableRequest


class DummyResponse(BaseModel):
    """测试用简单响应结构."""

    has_more: bool | None = None
    total: int | None = None
    items: list[Any] | None = None
    next_cursor: str | None = None


def test_page_strategy_has_next_and_next_params():
    """测试基于页码的分页策略 has_next 与 next_params."""
    strategy = PageStrategy[Any, DummyResponse](
        page_key="page",
        page_size=10,
        start_page=1,
        total_extractor=lambda r: r.total,
        has_more_extractor=lambda r: r.has_more,
    )
    # 当 has_more 显式提供时
    resp_flag = DummyResponse(has_more=True)
    assert strategy.has_next({"page": 1}, resp_flag) is True

    resp_no_flag = DummyResponse(has_more=False)
    assert strategy.has_next({"page": 1}, resp_no_flag) is False

    # 根据 total 判断
    resp_total = DummyResponse(has_more=None, total=25)
    assert strategy.has_next({"page": 1}, resp_total) is True
    assert strategy.has_next({"page": 3}, resp_total) is False

    # next_params 增量
    next_p = strategy.next_params({"page": 1}, resp_total)
    assert next_p["page"] == 2


def test_offset_strategy_has_next_and_next_params():
    """测试基于偏移量的分页策略 has_next 与 next_params."""
    strategy = OffsetStrategy[Any, DummyResponse](
        offset_key="start",
        page_size_key="size",
        start_offset=0,
        total_extractor=lambda r: r.total,
        count_extractor=lambda r: len(r.items) if r.items is not None else None,
    )

    resp = DummyResponse(total=30, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    params = {"start": 0, "size": 10}

    assert strategy.has_next(params, resp) is True

    next_p = strategy.next_params(params, resp)
    assert next_p["start"] == 10

    # 到底部
    last_params = {"start": 20, "size": 10}
    last_resp = DummyResponse(total=30, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert strategy.has_next(last_params, last_resp) is False

    # 当未提供 total/has_more 时, 安全返回 False 而非抛错
    empty_resp = DummyResponse(total=None)
    assert strategy.has_next(params, empty_resp) is False


def test_batch_refresh_strategy():
    """测试换一批策略 has_next 与 next_params."""
    strategy = BatchRefreshStrategy[Any, DummyResponse](
        refresh_key="vec",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    resp_more = DummyResponse(has_more=True, next_cursor="cur2")
    params = {"vec": "cur1"}

    assert strategy.has_next(params, resp_more) is True
    assert strategy.next_params(params, resp_more) == {"vec": "cur2"}

    # 当 has_more 为 None 但游标不同
    resp_none = DummyResponse(has_more=None, next_cursor="cur2")
    assert strategy.has_next(params, resp_none) is True

    # 游标相同
    same_params = {"vec": "cur2"}
    assert strategy.has_next(same_params, resp_more) is False


def test_cursor_strategy():
    """测试游标策略 has_next 与 next_params."""
    strategy = CursorStrategy[Any, DummyResponse](
        cursor_key="pos",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    resp = DummyResponse(has_more=True, next_cursor="100")
    params = {"pos": "0"}

    assert strategy.has_next(params, resp) is True
    assert strategy.next_params(params, resp) == {"pos": "100"}


def test_multi_field_continuation_strategy():
    """测试多字段延续策略 has_next 与 next_params."""

    def builder(p: dict[str, Any], r: DummyResponse) -> dict[str, Any] | None:
        if not r.items:
            return None
        return {**p, "page": p.get("page", 1) + 1}

    strategy = MultiFieldContinuationStrategy[Any, DummyResponse](builder)

    resp_has = DummyResponse(items=[1, 2])
    resp_empty = DummyResponse(items=[])

    params = {"page": 1}
    assert strategy.has_next(params, resp_has) is True
    assert strategy.next_params(params, resp_has) == {"page": 2}

    assert strategy.has_next(params, resp_empty) is False
    with pytest.raises(ValueError, match="分页响应未提供继续翻页所需的 continuation 数据"):
        strategy.next_params(params, resp_empty)


@pytest.mark.asyncio
async def test_paginated_request_paginate():
    """测试 PaginatedRequest 的 async for 迭代流程."""

    class DummyPaginatedRequest(PaginatedRequest):
        def __await__(self):
            async def _coro():
                return DummyResponse(total=20, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

            return _coro().__await__()

    strategy = OffsetStrategy[Any, DummyResponse](
        offset_key="start",
        page_size_key="size",
        total_extractor=lambda r: r.total,
    )

    req = DummyPaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"start": 0, "size": 10},
        pager_strategy=strategy,
    )

    results = [res async for res in req.paginate(limit=2)]
    assert len(results) == 2


def test_refreshable_request_next_request():
    """测试 RefreshableRequest 的 next_request 方法."""
    strategy = BatchRefreshStrategy[Any, DummyResponse](
        refresh_key="vec",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    req = RefreshableRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"vec": "cur1"},
        refresh_strategy=strategy,
    )

    resp_more = DummyResponse(has_more=True, next_cursor="cur2")
    next_req = req.next_request(resp_more)
    assert next_req is not None
    assert cast("dict[str, Any]", next_req.param)["vec"] == "cur2"

    resp_end = DummyResponse(has_more=False)
    assert req.next_request(resp_end) is None


@pytest.mark.asyncio
async def test_async_pager_and_collect_items():
    """测试 AsyncPager 控制器以及 PaginatedRequest 的 collect 与 iter_items 功能."""

    @dataclass
    class MockPaginatedRequest(PaginatedRequest[DummyResponse, int]):
        responses: list[DummyResponse] = field(default_factory=list)

        def __await__(self):
            async def _coro():
                start = cast("dict[str, Any]", self.param).get("start", 0)
                idx = start // 10
                if idx < len(self.responses):
                    return self.responses[idx]
                return DummyResponse(total=len(self.responses) * 10, items=[])

            return _coro().__await__()

    resp1 = DummyResponse(total=30, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    resp2 = DummyResponse(total=30, items=[11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    resp3 = DummyResponse(total=30, items=[21, 22, 23, 24, 25, 26, 27, 28, 29, 30])

    strategy_with_items = OffsetStrategy[Any, DummyResponse, int](
        offset_key="start",
        page_size=10,
        total_extractor=lambda r: r.total,
        items_extractor=lambda r: r.items,
    )

    req = MockPaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"start": 0},
        pager_strategy=strategy_with_items,
        responses=[resp1, resp2, resp3],
    )

    # 测试 pager 手动 step 推进与 limit
    pager = req.pager(limit=2)
    assert pager.has_more() is True
    page1 = await pager.next()
    assert page1.items == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    page2 = await pager.next()
    assert page2.items == [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    assert pager.has_more() is False
    with pytest.raises(StopAsyncIteration):
        await pager.next()

    # 测试 collect (页级别)
    pages = await req.collect(limit=2)
    assert len(pages) == 2

    # 测试 collect_items (条目级别)
    items_15 = await req.collect_items(limit=15)
    assert items_15 == list(range(1, 16))

    all_items = await req.collect_items()
    assert all_items == list(range(1, 31))

    # 测试未配置 items_extractor 触发 TypeError
    strategy_no_items = OffsetStrategy[Any, DummyResponse](
        offset_key="start",
        page_size=10,
        total_extractor=lambda r: r.total,
    )
    req_no_items = MockPaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"start": 0},
        pager_strategy=strategy_no_items,
        responses=[resp1],
    )
    with pytest.raises(TypeError, match="未配置 items_extractor"):
        await req_no_items.collect_items()


@pytest.mark.asyncio
async def test_async_refresher_and_stream():
    """测试 AsyncRefresher 控制器以及 RefreshableRequest 的 refresh_stream 与 aiter 功能."""

    @dataclass
    class MockRefreshableRequest(RefreshableRequest[DummyResponse, str]):
        response_map: dict[str, DummyResponse] = field(default_factory=dict)

        def __await__(self):
            async def _coro():
                cur = cast("dict[str, Any]", self.param).get("vec", "cur0")
                return self.response_map.get(cur, DummyResponse(items=[]))

            return _coro().__await__()

    resp1 = DummyResponse(has_more=True, next_cursor="cur1", items=["a", "b"])
    resp2 = DummyResponse(has_more=True, next_cursor="cur2", items=["c", "d"])
    resp3 = DummyResponse(has_more=False, next_cursor=None, items=["e", "f"])

    strategy = BatchRefreshStrategy[Any, DummyResponse, str](
        refresh_key="vec",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
        items_extractor=lambda r: r.items,
    )

    req = MockRefreshableRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"vec": "cur0"},
        refresh_strategy=strategy,
        response_map={"cur0": resp1, "cur1": resp2, "cur2": resp3},
    )

    # 测试 refresher 的 first 与 next
    refresher = req.refresher(limit=2)
    assert refresher.has_more() is True
    b1_first = await refresher.first()
    assert b1_first.items == ["a", "b"]
    b2 = await refresher.next()
    assert b2.items == ["c", "d"]
    b1_again = await refresher.first()
    assert b1_again.items == ["a", "b"]
    assert refresher.has_more() is False
    with pytest.raises(StopAsyncIteration):
        await refresher.next()

    # 测试 async for batch in req (aiter)
    batches = [batch async for batch in req]
    assert len(batches) == 3
    assert [b.items for b in batches] == [["a", "b"], ["c", "d"], ["e", "f"]]

    # 测试 collect_items
    items_3 = await req.collect_items(limit=3)
    assert items_3 == ["a", "b", "c"]
