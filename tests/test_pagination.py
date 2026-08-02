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
from qqmusic_api.core.request import (
    ItemPaginatedRequest,
    PaginatedRequest,
)


class DummyResponse(BaseModel):
    """测试用简单响应结构."""

    has_more: bool | None = None
    total: int | None = None
    items: list[Any] | None = None
    next_cursor: str | None = None


def test_page_strategy_has_next_and_next_params():
    """测试基于页码的分页策略 has_next 与 next_params."""
    strategy = PageStrategy[DummyResponse](
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
    strategy = OffsetStrategy[DummyResponse](
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
    strategy = BatchRefreshStrategy[DummyResponse](
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
    strategy = CursorStrategy[DummyResponse](
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

    strategy = MultiFieldContinuationStrategy[DummyResponse](builder)

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

    class DummyPaginatedRequest(PaginatedRequest[DummyResponse]):
        def __await__(self):
            async def _coro():
                return DummyResponse(total=20, items=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

            return _coro().__await__()

    strategy = OffsetStrategy[DummyResponse](
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


def test_batch_refresh_request_next_request():
    """测试 PaginatedRequest 配合 BatchRefreshStrategy 的 next_request 方法."""
    strategy = BatchRefreshStrategy[DummyResponse](
        refresh_key="vec",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    req = PaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"vec": "cur1"},
        pager_strategy=strategy,
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
    class MockPaginatedRequest(ItemPaginatedRequest[DummyResponse, int]):
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

    strategy = OffsetStrategy[DummyResponse](
        offset_key="start",
        page_size=10,
        total_extractor=lambda r: r.total,
    )

    req = MockPaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"start": 0},
        pager_strategy=strategy,
        items_extractor=lambda r: r.items,
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

    # 测试 items_extractor 返回 None 的处理
    req_none_items = MockPaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"start": 0},
        pager_strategy=strategy,
        items_extractor=lambda r: None,
        responses=[resp1],
    )
    items_none = await req_none_items.collect_items()
    assert items_none == []


@pytest.mark.asyncio
async def test_async_pager_with_batch_refresh_strategy():
    """测试 AsyncPager 控制器 (含 first/next) 以及配合 BatchRefreshStrategy 的工作功能."""

    @dataclass
    class MockPaginatedRequest(ItemPaginatedRequest[DummyResponse, str]):
        response_map: dict[str, DummyResponse] = field(default_factory=dict)

        def __await__(self):
            async def _coro():
                cur = cast("dict[str, Any]", self.param).get("vec", "cur0")
                return self.response_map.get(cur, DummyResponse(items=[]))

            return _coro().__await__()

    resp1 = DummyResponse(has_more=True, next_cursor="cur1", items=["a", "b"])
    resp2 = DummyResponse(has_more=True, next_cursor="cur2", items=["c", "d"])
    resp3 = DummyResponse(has_more=False, next_cursor=None, items=["e", "f"])

    strategy = BatchRefreshStrategy[DummyResponse](
        refresh_key="vec",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
    )

    req = MockPaginatedRequest(
        _client=cast("Any", None),
        module="test",
        method="test",
        param={"vec": "cur0"},
        pager_strategy=strategy,
        items_extractor=lambda r: r.items,
        response_map={"cur0": resp1, "cur1": resp2, "cur2": resp3},
    )

    # 测试 pager 的 first 与 next
    pager = req.pager(limit=2)
    assert pager.has_more() is True
    b1_first = await pager.first()
    assert b1_first.items == ["a", "b"]
    b2 = await pager.next()
    assert b2.items == ["c", "d"]
    b1_again = await pager.first()
    assert b1_again.items == ["a", "b"]
    assert pager.has_more() is False
    with pytest.raises(StopAsyncIteration):
        await pager.next()

    # 测试 limit=0 时 first() 短路抛出 StopAsyncIteration
    pager_zero = req.pager(limit=0)
    assert pager_zero.has_more() is False
    with pytest.raises(StopAsyncIteration):
        await pager_zero.first()

    # 测试 async for batch in req (aiter)
    batches = [batch async for batch in req]
    assert len(batches) == 3
    assert [b.items for b in batches] == [["a", "b"], ["c", "d"], ["e", "f"]]

    # 测试 collect_items
    items_3 = await req.collect_items(limit=3)
    assert items_3 == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_with_extractor_combinator():
    """测试通过 with_extractor 动态注入数据项提取器."""
    strategy = PageStrategy[DummyResponse](
        page_key="page",
        page_size=10,
        start_page=1,
        total_extractor=lambda r: r.total,
        has_more_extractor=lambda r: r.has_more,
    )

    resp1 = DummyResponse(total=30, has_more=True, items=[1, 2, 3])
    resp2 = DummyResponse(total=30, has_more=False, items=[4, 5, 6])

    class MockClient:
        async def execute(self, req: Any) -> DummyResponse:
            page = req.param["page"]
            return resp1 if page == 1 else resp2

    req = PaginatedRequest(
        _client=cast("Any", MockClient()),
        module="test",
        method="test",
        param={"page": 1},
        response_model=cast("Any", None),
        pager_strategy=strategy,
    )

    item_req = req.with_extractor(lambda r: r.items or [])
    assert isinstance(item_req, ItemPaginatedRequest)

    items = await item_req.collect_items()
    assert items == [1, 2, 3, 4, 5, 6]


@pytest.mark.asyncio
async def test_page_strategy_count_fallback():
    """测试 PageStrategy 仅配置 count_extractor 和 page_size 时依据数据条目数终止翻页."""
    strategy = PageStrategy[DummyResponse](
        page_key="page",
        page_size=10,
        start_page=1,
        count_extractor=lambda r: len(r.items or []),
    )

    resp1 = DummyResponse(items=list(range(10)))
    resp2 = DummyResponse(items=[1, 2, 3])

    assert strategy.has_next({"page": 1}, resp1) is True
    assert strategy.has_next({"page": 2}, resp2) is False


@pytest.mark.asyncio
async def test_cursor_strategy_short_circuit_has_more():
    """测试 CursorStrategy 在 has_more 为 True 时短路判定未终止, 不被少量条目误判."""
    strategy = CursorStrategy[DummyResponse](
        cursor_key="cursor",
        cursor_extractor=lambda r: r.next_cursor,
        has_more_extractor=lambda r: r.has_more,
        count_extractor=lambda r: len(r.items or []),
        page_size=10,
    )

    resp = DummyResponse(has_more=True, items=[1, 2], next_cursor="next_c")
    assert strategy.has_next({"cursor": "init_c"}, resp) is True
